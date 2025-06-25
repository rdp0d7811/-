channels = [
    {
        "name": "OnSide Sport | بثوث المباريات",
        "link": "https://t.me/+z1RmEKNsagRiODky",
        "chat_id": -1002004465773
    },
    
]

def get_not_joined_channels(bot, user_id):
    not_joined = []
    for ch in channels:
        try:
            member = bot.get_chat_member(ch["chat_id"], user_id)
            if member.status in ["left", "kicked"]:
                not_joined.append(ch)
        except:
            not_joined.append(ch)
    return not_joined
