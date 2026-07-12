/**
 * functions/index.js
 *
 * Watches the Firestore "applications" collection. Whenever the
 * parent app writes a new application, this automatically sends
 * a confirmation email — to the parent (if they gave an email
 * address) and a copy to your own admin inbox.
 *
 * WHY THIS LIVES HERE AND NOT IN THE HTML FILE
 * ---------------------------------------------
 * Your email password can never appear in school-registration-app.html
 * or admin.html — anyone who views the page source (or your public
 * GitHub repo) would see it instantly. Cloud Functions run on
 * Google's servers, not in the browser, so this is the only safe
 * place for it. Even here, the actual password lives in a separate
 * .env file that is NEVER committed to git (see .gitignore).
 */

const { onDocumentCreated } = require("firebase-functions/v2/firestore");
const { defineString, defineSecret } = require("firebase-functions/params");
const admin = require("firebase-admin");
const nodemailer = require("nodemailer");

admin.initializeApp();

// Non-secret settings (safe to be plain text)
const MAIL_SERVER = defineString("MAIL_SERVER", { default: "smtp.gmail.com" });
const MAIL_PORT = defineString("MAIL_PORT", { default: "587" });
const MAIL_USERNAME = defineString("MAIL_USERNAME");
const ALERT_EMAIL = defineString("ALERT_EMAIL");

// Secret setting — the actual password, stored encrypted by
// Firebase, never visible in your code or your repo.
const MAIL_PASSWORD = defineSecret("MAIL_PASSWORD");

exports.sendApplicationEmail = onDocumentCreated(
  { document: "applications/{ref}", secrets: [MAIL_PASSWORD] },
  async (event) => {
    const data = event.data.data();
    if (!data) return;

    const transporter = nodemailer.createTransport({
      host: MAIL_SERVER.value(),
      port: Number(MAIL_PORT.value()),
      secure: false, // true for port 465, false for 587 (TLS via STARTTLS)
      auth: {
        user: MAIL_USERNAME.value(),
        pass: MAIL_PASSWORD.value(),
      },
    });

    const subject = `Vulani application received — ${data.ref}`;
    const bodyLines = [
      `Hi ${data.pName || "there"},`,
      ``,
      `We've received the application for ${data.cName} (${data.cGrade}) at ${data.school?.name || "the selected school"}.`,
      ``,
      `Reference number: ${data.ref}`,
      `Submitted: ${data.submitted}`,
      ``,
      `Keep this reference number safe — the school will be in touch on ${data.pPhone} once a place is confirmed.`,
      `No payment is ever required at any step.`,
      ``,
      `— Vulani`,
    ];
    const text = bodyLines.join("\n");

    // Email the parent, only if they gave us an address
    if (data.pEmail) {
      try {
        await transporter.sendMail({
          from: MAIL_USERNAME.value(),
          to: data.pEmail,
          subject,
          text,
        });
      } catch (err) {
        console.error("Failed to email parent:", err);
      }
    }

    // Always email your own admin inbox as a live notification
    try {
      await transporter.sendMail({
        from: MAIL_USERNAME.value(),
        to: ALERT_EMAIL.value(),
        subject: `New application: ${data.cName} — ${data.ref}`,
        text: `${text}\n\nParent phone: ${data.pPhone}\nParent email: ${data.pEmail || "(not provided)"}`,
      });
    } catch (err) {
      console.error("Failed to email admin alert:", err);
    }
  }
);
