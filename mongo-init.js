// mongo-init.js
db.createUser({
  user: "uav_user",
  pwd: "uav_password",
  roles: [
    {
      role: "readWrite",
      db: "uav_restoration"
    }
  ]
});