from telethon import TelegramClient, events
import asyncio
import random

# وارد کردن API ID و API Hash
api_id = 26665370 
api_hash = '19323431934da1ab20b8f3247c3bdc96'

client = TelegramClient('my_session', api_id, api_hash)

# صف پیام‌ها برای گروه‌ها
group_message_queue = asyncio.Queue()
group_processing_active = True  # فعال یا غیرفعال بودن پردازش پیام‌های گروه
group_semaphore = asyncio.Semaphore(10)  # محدود کردن تعداد پردازش همزمان پیام‌های گروه

# مجموعه کاربران پاسخ داده‌شده در چت خصوصی
private_responded_users = set()

# پیام‌های تصادفی برای ریپلای به گروه‌ها
group_messages = [
    "سلام عزیزم! یه ذره وقت آزاد داری؟ می‌خوام باهات مشورت کنم 🌸"

"هی قشنگم، میشه یه دقیقه بِگیسمت؟ سوال کوچیکی دارم 💌"

"دلَم برات تنگ شده! می‌تونی الان چند لحظه بهم توجه کنی؟ 😊"

"جانم، یه لطفِ کوچولو ازت می‌خوام… می‌شه کمکم کنی؟ 🤲"

"سلام نازنین! میدونم شلوغی، ولی میشه یه لحظه همدیگه رو داشته باشیم؟ 💞"

"عزیزم، میخوام یه راز کوچیکو بهت بگم… میشه گوش بدی؟ 🤫"

"پیشونی سفیدت! یه کار فوری دارم، می‌شه قربونت برم کمک کنی؟ 🥺"

"سلام فرشتهگلم! یه ذره حوصله داری برات دردِدل کنم؟ 🌙"

"چشماتو قشنگتر از این حرفاست! میشه روشونو به جوابم بدی؟ 😇"

"جانِ جونم، منو تنها نذار! یه موضوع مهم دارم باهات 💬"

"قشنگِ قشنگ! میدونم شاید مزاحم شم، ولی واقعاً نیاز دارم بهت 🙏"

"نفسم! میتونی یه ذره از وقتِ گرونیتو بهم هدیه بدی؟ 💎"

"سلام گلم! اگه الان آزادی، بیا باهم یه کاری رو سریع تموم کنیم �"

"عزیزِ آسمونی! یه همکاریِ کوچولو میخوام… قول میدم کم باشه! 🤝"

"پیشونی خوشگل! چرا جواب نمیدی؟ منتظرم مثل گل پژمردم 😢"

"دوستِ نازنینم، میدونی چقدر به راهنماییت نیاز دارم؟ لطفاً کمکم کن 🌟"

"قربونت برم عزیزم! یه کارِ دو دقیقه‌ایه، می‌شه انجامش بدی؟ ⏳"

"چشمای قشنگت رو میبوسم! میشه یه ذره بهم محبت کنی؟ 😘"

"نازدستاتو میبوسم! میخوام یه کمکت کنم، میشه بگی چطوری؟ 💐"

"خورشیدِ زندگیم! الان وقت داری باهم یه فکری بکنیم؟ ☀️"

"گُلسُفتِ من! چرا انقدر دیر جواب میدی؟ دلم برات تنگ شده 😞"

"همدمِ قشنگم، میشه یه کم آرومتر بشینیم و حرف بزنیم؟ 🍵"

"عزیزم، اگه الان مشغولی بگو بعداً بیام… ولی خیلی دلم گرفته 🕊️"

"پریِ نازنین! میدونم خسته‌ای، ولی میشه یه ذره هم به فکر من باشی؟ 🌼"

"جانم، دستِ خوشگلت درد نکنه! میشه یه کارِ کوچیک برام بکنی؟ 🤲"

"قشنگِ دنیا! میخوام بدونم نظرت چیه… میشه راهنماییم کنی؟ 💭"

"آقا/خانمِ مهربون! اگه راحتید میشه یه ذره هم به من توجه کنید؟ 🌷"

"عزیزم، یه لطفِ بزرگ میخوام… میدونم میتونی کمکم کنی! 💪"

"همیشه بهت تو دلُم گرمه! میشه امروز تو هم بهم گرمی بدی؟ ❤️"

"نازنینم، اگه جواب ندی مجبورم شمع بسازم و اشک بریزم 🕯️😂"

"پیشونی بَشّاش! چرا حوصله نداری؟ بیا باهم یه کاری کنیم 😄"

"دوستِ خوشمزه! میدونم وقتت کمه، ولی منو دریاب لطفاً 🍩"

"همراهِ همیشگی! امروز بیشتر از همیشه بهت نیاز دارم… 💔"

"عزیزم، اگه یه دقیقه وقت بدی، دنیامو میسازی! 🌈"

"میخوام مثل همیشه بهت تکیه کنم… میشه دستم رو بگیري؟ 🤲"

"قشنگِ قشنگ! اگه جواب ندی مجبورم اسمتو بذارم تو شعرام 📜"

"نفسم، میدونی چقدر به حمایتت نیاز دارم؟ لطفاً تنهام نذار 🥀"

"دلبرِ من! یه موضوعِ شیرین دارم باهات… میشه گوش بدی؟ 🍯"

"همدمِ عزیزم، اگه الان آزادی بیا باهم یه فکری بکنیم 🤗"

"عزیزِ دلم، اگه جواب بدی قول میدم فردا برات کیک بپزم! 🎂"
]


# تابع مدیریت وقفه‌های گروه
async def manage_group_pause():
    global group_processing_active
    while True:
        print("Group processing active for 15 minutes...")
        group_processing_active = True
        await asyncio.sleep(300)  # 15 دقیقه فعال

        print("Pausing group processing for 5 minutes...")
        group_processing_active = False
        await asyncio.sleep(150)  # 5 دقیقه غیرفعال

# تابع پردازش پیام‌های گروه
async def process_group_messages():
    while True:
        event = await group_message_queue.get()
        try:
            if group_processing_active:
                async with group_semaphore:  # محدودیت تعداد پردازش همزمان
                    random_message = random.choice(group_messages)
                    await client.send_message(event.chat_id, random_message, reply_to=event.id)
                    print(f"Replied to group message: {random_message}")
        except Exception as e:
            print(f"Failed to process group message: {e}")
        finally:
            group_message_queue.task_done()

# متد اصلی برای راه‌اندازی ربات
async def main():
    await client.start()
    print("Bot started successfully!")

    # شروع مدیریت وقفه‌ها و پردازش پیام‌های گروه
    asyncio.create_task(manage_group_pause())
    asyncio.create_task(process_group_messages())

    @client.on(events.NewMessage)
    async def handler(event):
        if event.is_private:  # پیام چت خصوصی
            user_id = event.sender_id
            if user_id not in private_responded_users:  # بررسی پاسخ ندادن قبلی
                try:
                    await client.send_message(event.chat_id, "https://t.me/IR_DARO")
                    private_responded_users.add(user_id)
                    print(f"Replied to private message from user: {user_id}")
                except Exception as e:
                    print(f"Failed to reply to private message: {e}")

        elif event.is_group:  # پیام گروه
            if group_message_queue.qsize() < 50:  # محدود کردن تعداد پیام‌های در صف
                await group_message_queue.put(event)
                print(f"Added group message to queue: {event.chat_id}")
            else:
                print("Group message queue full. Ignoring new message.")

    


    await client.run_until_disconnected()

with client:
    client.loop.run_until_complete(main())
