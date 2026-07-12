EMAIL NOTIFICATIONS — SETUP STEPS
==================================

You'll need Node.js installed (you already have Python; check Node
with "node --version" in Command Prompt — if missing, get it from
nodejs.org, the LTS version).

1. Install the Firebase command line tool (once):
     npm install -g firebase-tools

2. Sign in:
     firebase login

3. From inside your V folder, connect this project to your Firebase
   project (the same one your app already uses):
     firebase init functions
   When asked:
     - "Use an existing project" -> pick the same Firebase project
       you created earlier
     - Language: JavaScript
     - Overwrite files: say NO if it asks about index.js or
       package.json — you already have the real ones I wrote for you

4. Copy .env.example to .env inside the functions folder, and fill
   in your real (NEW, rotated) Gmail address:
     MAIL_USERNAME=your-real-address@gmail.com
     ALERT_EMAIL=your-real-address@gmail.com

5. Set the password as a Firebase SECRET (not plain text) — run this
   in Command Prompt and paste your NEW app password when prompted:
     firebase functions:secrets:set MAIL_PASSWORD

6. Install the function's dependencies:
     cd functions
     npm install
     cd ..

7. Deploy:
     firebase deploy --only functions

   Note: Cloud Functions requires Firebase's "Blaze" (pay-as-you-go)
   plan, not the free "Spark" plan — because sending email means
   reaching an outside server (Gmail), which Spark doesn't allow.
   Blaze still has a generous free monthly allowance; for a pilot
   sending a handful of emails a day, you are extremely unlikely to
   be charged anything. Firebase will prompt you to upgrade the
   first time you try to deploy if you haven't already.

8. Test it: submit a test application through school-registration-app.html
   with a real email address in the (new) "Email address" field —
   you should get a confirmation email within a few seconds, and
   your ALERT_EMAIL inbox should get a copy too.

Gmail-specific note: Gmail requires an "app password" (not your
normal login password) for this kind of automated sending, and only
works this way if 2-Step Verification is turned on for the account.
That's what myaccount.google.com/apppasswords generates.
