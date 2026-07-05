from datetime import datetime
import threading
import logging
from app.extensions import db, socketio
from app.models.token import Token
from app.models.counter import Counter
from app.services.ai_service import AiService
from app.monitoring import queue_length_gauge

logger = logging.getLogger("flask.app")

def update_queue_length_metric():
    waiting_count = Token.query.filter_by(status="waiting").count()
    queue_length_gauge.set(waiting_count)

def background_ai_update(queue_lengths, avg_times, service_type, service_duration, done_count):
    try:
        reward = -service_duration
        # Update RL tables
        AiService.update_rl_tables(queue_lengths, avg_times, service_type, 0, reward)
        # Retrain ML model periodically
        if done_count % 100 == 0 and done_count > 0:
            AiService.trigger_model_retraining()
            logger.info("AI Model retrained successfully in background", extra={"done_count": done_count})
    except Exception as e:
        logger.error(f"AI Update Error in background thread: {e}", exc_info=True)

class QueueService:
    @staticmethod
    def get_avg_time(counter_id):
        completed = Token.query.filter_by(counter_id=counter_id, status="done").all()
        if not completed:
            return 5.0
            
        total = 0.0
        valid_count = 0
        for t in completed:
            start = t.start_time or t.arrival_time
            if start and t.end_time:
                duration = (t.end_time - start).total_seconds() / 60.0
                total += duration
                valid_count += 1
                
        if valid_count > 0:
            return total / valid_count
        return 5.0

    @staticmethod
    def create_token(service_type):
        counters = Counter.query.filter_by(service_type=service_type, status="open").all()
        if not counters:
            return None, "No counters available for this service"
            
        queue_lengths = []
        avg_times = []
        for counter in counters:
            queue_len = Token.query.filter_by(counter_id=counter.id, status="waiting").count()
            queue_lengths.append(queue_len)
            avg_times.append(QueueService.get_avg_time(counter.id))
            
        action = AiService.choose_optimal_counter(queue_lengths, avg_times, service_type, counters)
        best_counter = counters[action]
        
        total_tokens = Token.query.count()
        token_number = f"T{total_tokens + 1}"
        
        token = Token(
            token_number=token_number,
            service_type=service_type,
            counter_id=best_counter.id
        )
        
        db.session.add(token)
        db.session.commit()

        update_queue_length_metric()
        
        service_code = AiService.encode_service_type(service_type)
        queue_length = Token.query.filter_by(counter_id=best_counter.id, status="waiting").count()
        waiting_time = AiService.predict_waiting_time(
            queue_length,
            best_counter.id,
            service_code,
            QueueService.get_avg_time(best_counter.id)
        )
        
        # Notify clients
        socketio.emit("queue_update", {"message": "New token created"})
        
        # Log event
        logger.info(
            "Token created", 
            extra={
                "token_number": token_number, 
                "service_type": service_type, 
                "counter": best_counter.name,
                "waiting_time": waiting_time
            }
        )
        
        return {
            "token": token_number,
            "counter": best_counter.name,
            "waiting_time": f"{waiting_time} minutes"
        }, None

    @staticmethod
    def get_next_token(counter_id):
        serving_token = Token.query.filter_by(counter_id=counter_id, status="serving").first()
        if serving_token:
            return {
                "token_id": serving_token.id,
                "token_number": serving_token.token_number,
                "is_serving": True
            }, None
            
        token = Token.query.filter_by(counter_id=counter_id, status="waiting").order_by(Token.arrival_time).first()
        if not token:
            return {"message": "No waiting tokens"}, None
            
        return {
            "token_id": token.id,
            "token_number": token.token_number,
            "is_serving": False
        }, None

    @staticmethod
    def get_waiting_tokens(counter_id):
        tokens = Token.query.filter_by(counter_id=counter_id, status="waiting").order_by(Token.arrival_time).all()
        return [{"id": t.id, "token_number": t.token_number} for t in tokens]

    @staticmethod
    def get_live_board():
        counters = Counter.query.order_by(Counter.id).all()
        board_data = []
        for c in counters:
            current_token = Token.query.filter_by(counter_id=c.id, status="serving").first()
            waiting_tokens = Token.query.filter_by(counter_id=c.id, status="waiting").order_by(Token.arrival_time).all()
            
            board_data.append({
                "id": c.id,
                "name": c.name,
                "service_type": c.service_type,
                "status": c.status,
                "current_token": current_token.token_number if current_token else None,
                "waiters": [{"id": t.id, "token_number": t.token_number} for t in waiting_tokens],
                "waiting_count": len(waiting_tokens)
            })
        return board_data

    @staticmethod
    def start_service(token_id):
        token = Token.query.get(token_id)
        if not token:
            return False, "Token not found"
            
        token.status = "serving"
        token.start_time = datetime.utcnow()
        db.session.commit()

        update_queue_length_metric()
        
        socketio.emit("queue_update", {"message": "Service started"})
        
        logger.info("Service started", extra={"token_id": token_id, "token_number": token.token_number})
        return True, None

    @staticmethod
    def finish_service(token_id):
        token = Token.query.get(token_id)
        if not token:
            return False, "Token not found"
            
        token.status = "done"
        token.end_time = datetime.utcnow()
        db.session.commit()

        update_queue_length_metric()
        
        if not token.start_time:
            token.start_time = token.arrival_time
            
        service_duration = (token.end_time - token.start_time).total_seconds() / 60.0
        
        counters = Counter.query.filter_by(service_type=token.service_type).all()
        queue_lengths = []
        avg_times = []
        for counter in counters:
            q = Token.query.filter_by(counter_id=counter.id, status="waiting").count()
            queue_lengths.append(q)
            avg_times.append(service_duration)
            
        done_count = Token.query.filter_by(status="done").count()
        
        # Start AI updates on background thread
        thread = threading.Thread(
            target=background_ai_update,
            args=(queue_lengths, avg_times, token.service_type, service_duration, done_count)
        )
        thread.start()
        
        socketio.emit("queue_update", {"message": "Service finished"})
        
        logger.info(
            "Service finished", 
            extra={
                "token_id": token_id, 
                "token_number": token.token_number, 
                "duration_minutes": service_duration
            }
        )
        return True, None

    @staticmethod
    def current_token(counter_id):
        token = Token.query.filter_by(counter_id=counter_id, status="serving").first()
        if not token:
            return None
        return token.token_number
