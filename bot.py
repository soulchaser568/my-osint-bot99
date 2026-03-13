import requests
import logging
import time
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = "8037332460:AAHlSCAQTPR4jLylYngzoAXlcohdvllScCE"
NUMBER_API = "https://all.proportalxc.workers.dev/number?number="
VEHICLE_API = "https://org.proportalxc.workers.dev/?rc="
ADMIN_ID = 5192884021

logging.basicConfig(
    filename="bot.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

user_last_request = {}

def allowed(user_id):
    now = time.time()
    last = user_last_request.get(user_id, 0)
    if now - last < 5:
        return False
    user_last_request[user_id] = now
    return True


keyboard = [["📱 Number Lookup"], ["🚗 Vehicle Lookup"]]
reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Select Lookup Service",
        reply_markup=reply_markup
    )


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

    user_id = update.effective_user.id

    if not allowed(user_id):
        await update.message.reply_text("⏱ Slow down.")
        return

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
            r = requests.get(f"{NUMBER_API}{text}")
            data = r.json()["result"][0]

            msg = f"""
API Developer : @h4ckerrmx
Developer     : @h4ckerrmx

📞 Mobile No     : {data.get("mobile")}
👨 Name          : {data.get("name")}
👴 Father Name   : {data.get("father_name")}
🏠 Address       : {data.get("address")}
🖄 Aadhaar ID    : {data.get("aadhaar")}
📱 Alt Mobile    : {data.get("alternate_number")}
📍 Circle        : {data.get("circle")}
📧 Email         : {data.get("email")}
"""

            await update.message.reply_text(msg)

            await notify_admin(update, context, "Number Lookup", text)

        except Exception as e:
            logging.error(e)
            await update.message.reply_text("Lookup failed.")


# -------- VEHICLE LOOKUP --------

    elif mode == "veh":

        try:
            r = requests.get(f"{VEHICLE_API}{text}")
            js = r.json()
            d = js.get("data", {})

            owner = d.get("custodian_profile_analytics", {}).get("legal_owner")
            city = d.get("custodian_profile_analytics", {}).get("city_node")
            address = d.get("custodian_profile_analytics", {}).get("geo_location")

            rc = d.get("identity_matrix_secure", {}).get("rc_number")

            engine = d.get("engineering_specification_vault", {}).get("engine_block_id")
            chassis = d.get("engineering_specification_vault", {}).get("chassis_integrity")

            insurance = d.get("protection_security_audit", {}).get("insurance_status")
            challan = d.get("legal_compliance_vault", {}).get("pending_challan_est")
            theft = d.get("legal_compliance_vault", {}).get("theft_database_check")

            market_value = d.get("asset_valuation_economics", {}).get("fair_market_value")
            idv = d.get("asset_valuation_economics", {}).get("insurance_idv_estimate")
            resale = d.get("asset_valuation_economics", {}).get("resale_probability")

            future_value = d.get("predictive_future_analytics", {}).get("future_value_2yr_projection")

            engine_eff = d.get("diagnostic_health_matrix", {}).get("engine_thermal_efficiency")
            battery = d.get("diagnostic_health_matrix", {}).get("battery_load_test")
            brakes = d.get("diagnostic_health_matrix", {}).get("brake_pad_density")

            fastag = d.get("toll_fastag_intelligence", {}).get("tag_status")
            bank = d.get("toll_fastag_intelligence", {}).get("issuer_bank")

            try:
                health_score = float(engine_eff.replace("%",""))/10
            except:
                health_score = "N/A"

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

💰 Market Value : {market_value}
📉 IDV Estimate : {idv}
📊 Resale Probability : {resale}
💰 Future Value (2yr) : {future_value}

⚙ Engine Efficiency : {engine_eff}
🔋 Battery Test : {battery}
🛞 Brake Pads : {brakes}

🚗 Vehicle Health Score : {health_score} / 10

🏷 FASTag : {fastag}
🏦 Issuer Bank : {bank}
"""

            await update.message.reply_text(msg)

            await notify_admin(update, context, "Vehicle Lookup", text)

        except Exception as e:
            logging.error(e)
            await update.message.reply_text("Vehicle lookup failed.")


app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

print("Bot running...")

app.run_polling()
