require("dotenv-safe").config();

import * as admin from "firebase-admin"
admin.initializeApp({
  credential: admin.credential.cert("firebase-key.json")
});

admin.messaging().send