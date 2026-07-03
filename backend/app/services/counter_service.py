from app.extensions import db, socketio
from app.models.counter import Counter

class CounterService:
    @staticmethod
    def add_counter(name, service_type):
        counter = Counter(name=name, service_type=service_type)
        db.session.add(counter)
        db.session.commit()
        
        # Emit real-time updates
        socketio.emit("queue_update", {"message": "Counter added"})
        return counter

    @staticmethod
    def get_all_counters():
        return Counter.query.all()

    @staticmethod
    def delete_counter(counter_id):
        counter = Counter.query.get(counter_id)
        if not counter:
            return False, "Counter not found"
            
        db.session.delete(counter)
        db.session.commit()
        
        # Emit real-time updates
        socketio.emit("queue_update", {"message": "Counter deleted"})
        return True, None
