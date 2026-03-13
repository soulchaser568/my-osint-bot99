import requests
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = "8037332460:AAHlSCAQTPR4jLylYngzoAXlcohdvllScCE"
ADMIN_ID = 5192884021

NUMBER_API = "https://all.proportalxc.workers.dev/number?number="
RC_API = "https://org.proportalxc.workers.dev/?rc="

HEADERS = {"User-Agent": "Mozilla/5.0"}

keyboard = [["📱 Number Lookup"], ["🚗 Vehicle Lookup"]]
reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Select Lookup Service", reply_markup=reply_markup)


async def notify_admin(update, context, lookup_type, query):
    user = update.effective_user
    username = user.username if user.username else "NoUsername"

    msg = f"""
🚨 BOT LOOKUP ALERT

👤 Name : {user.first_name}
🔗 Username : @{username}
🆔 User ID : {user.id}

🔍 Type : {lookup_type}
📄 Query : {query}
"""
    await context.bot.send_message(chat_id=ADMIN_ID, text=msg)


async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text.strip()

    if text == "📱 Number Lookup":
        context.user_data["mode"] = "num"
        await update.message.reply_text("Send Mobile Number")
        return

    if text == "🚗 Vehicle Lookup":
        context.user_data["mode"] = "veh"
        await update.message.reply_text("Send Vehicle Number")
        return

    mode = context.user_data.get("mode")


    # -------- NUMBER LOOKUP --------
    if mode == "num":
        try:
            r = requests.get(NUMBER_API + text, headers=HEADERS)
            js = r.json()

            results = js.get("result", {}).get("result", [])

            if not results:
                await update.message.reply_text("No data found")
                return

            data = results[0]

            mobile = data.get("mobile")
            name = data.get("name")
            father = data.get("father_name")

            address = data.get("address", "")
            address = address.replace("!", " ").replace("|", " ")

            circle = data.get("circle/sim")
            alt = data.get("alternative_mobile")
            aadhaar = data.get("aadhar_number")
            email = data.get("email")

            msg = f"""
API Developer : @h4ckerrmx
Developer     : @h4ckerrmx

📞 Mobile No     : {mobile}
👨 Name          : {name}
👴 Father Name   : {father}
🏠 Address       : {address}
🖄 Aadhaar ID    : {aadhaar}
📱 Alt Mobile    : {alt}
📍 Circle        : {circle}
📧 Email         : {email}
"""

            await update.message.reply_text(msg)
            await notify_admin(update, context, "Number Lookup", text)

        except Exception as e:
            print(e)
            await update.message.reply_text("Lookup failed")


    # -------- RC LOOKUP --------
    elif mode == "veh":
        try:
            r = requests.get(RC_API + text, headers=HEADERS)
            js = r.json()

            d = js.get("data", {})

            rc = d.get("identity_matrix_secure", {}).get("rc_number")
            owner = d.get("custodian_profile_analytics", {}).get("legal_owner")
            city = d.get("custodian_profile_analytics", {}).get("city_node")
            address = d.get("custodian_profile_analytics", {}).get("geo_location")

            engine = d.get("engineering_specification_vault", {}).get("engine_block_id")
            chassis = d.get("engineering_specification_vault", {}).get("chassis_integrity")

            insurance = d.get("protection_security_audit", {}).get("insurance_status")
            challan = d.get("legal_compliance_vault", {}).get("pending_challan_est")
            theft = d.get("legal_compliance_vault", {}).get("theft_database_check")

            msg = f"""
API Developer : @h4ckerrmx
Developer     : @h4ckerrmx

🚗 RC Number : {rc}
👤 Owner : {owner}
🏙 City : {city}
📍 Address : {address}

🔧 Engine : {engine}
🧾 Chassis : {chassis}

🛡 Insurance : {insurance}
🚨 Pending Challan : {challan}
🔐 Theft Status : {theft}
"""

            await update.message.reply_text(msg)
            await notify_admin(update, context, "Vehicle Lookup", text)

        except Exception as e:
            print(e)
            await update.message.reply_text("RC lookup failed")


app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

print("Bot running...")

app.run_polling()
