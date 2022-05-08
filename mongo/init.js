db = new Mongo().getDB("Registry");

db.createUser({
    user: 'registry',
    pwd: 'PiRegistry_2022',
    roles: [
        {
            role: 'readWrite',
            db: 'PiRegistry',
        },
    ],
});

// Everything here can be discussed
db.createCollection('Tasks', {capped: false});
db.createCollection('Pipelines', {capped: false});

// Not all ids have to be like that
db.Tasks.createIndex({ "id": 1, "createdAt": 1 }, { unique: false });
db.Pipelines.createIndex({"id": 1, "createdAt": 1}, {unique: false});

db.Tasks.insert([{"id": "123"}])