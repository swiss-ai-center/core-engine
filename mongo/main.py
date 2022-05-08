from mongo_driver.MongoDriver import MongoDriver
from mongo_driver.models.Task import Task

# Get tasks from the database
def get_tasks(task_id: str, limit: int = 300) -> Task:
	# You can also use the ["name"] to select a collection :
	# collection = self.database["Tasks"]
	collection = driver.get_collection("Tasks")
	result = collection.find({"id": task_id})

	print([Task.parse_obj(i) for i in result])


# Update or insert an object. If the id of the task already exists,
# the document will be updated with the given data
def upsert_something(task: Task):
	collection = driver.get_collection("Tasks")
	query: dict = task.dict()
	update: dict = {"$set": query}
	collection.update_one(query, update, upsert=True)

def get_all_tasks():
	collection = driver.get_collection("Tasks")
	result = collection.find()

	print([Task.parse_obj(i) for i in result])


if __name__ == "__main__":
	driver = MongoDriver()

	get_tasks("123")

	upsert_something(Task(id="234"))

	get_tasks("234")

	get_all_tasks()

	driver.close()
