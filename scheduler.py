import datetime
from utils import send_reminder_email
import config


def check_due_reminders():
    today = datetime.date.today()
    for v in volunteers:
        for shot in shots:
            last_date_str = v["shots"].get(shot["id"])
            if last_date_str:
                last_date = datetime.datetime.strptime(last_date_str, "%Y-%m-%d").date()
                next_due = last_date + datetime.timedelta(days=shot["frequency"])

                # Debug print to check overdue logic
                if next_due <= today:
                    print(
                        f"Would send email to {v['email']} and {config.DEFAULT_NOTIFICATION_EMAIL} for {shot['name']} overdue on {next_due}")

                    subject = f"Reminder: {shot['name']} due for {v['name']}"
                    volunteer_body = (
                        f"Dear {v['name']},\n"
                        f"You are due for your {shot['name']} since {next_due}. Please take this shot as soon as possible."
                    )
                    admin_body = (
                        f"{v['name']} ({v['email']}) is due for their {shot['name']} (due {next_due}).\n"
                        f"Last given: {last_date_str}\n"
                    )
                    # Uncomment these when you're ready to send real emails:
                    # send_reminder_email(v["email"], subject, volunteer_body)
                    # send_reminder_email(config.DEFAULT_NOTIFICATION_EMAIL, subject, admin_body)
                    print(f"Sent reminders (Admin & Volunteer) for {v['name']}: {shot['name']} due {next_due}")


if __name__ == "__main__":
    check_due_reminders()
