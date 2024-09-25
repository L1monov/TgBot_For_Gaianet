from openai import OpenAI
from TelegramBot.settings.config import GAIANET_URL

client = OpenAI(base_url=GAIANET_URL)

async def generate_short_description(full_description: str):
    """
    Function that generates a short summary (250-300 characters) of the event description,
    keeping key details like speakers, sponsors, and organizers.

    :param full_description: Full text of the event description
    :return: Summary of the event, excluding name, date, time, location, and link
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"I need a summary of the event information. The final message should be 250-300 characters long, keeping the key details: speakers, sponsors, organizers. Do not include the event name, date, time, location, link. Focus on providing only the main details and purpose of the event in a concise format. Here is the text to process: {full_description}"}
        ]
    )
    return response.choices[0].message.content
