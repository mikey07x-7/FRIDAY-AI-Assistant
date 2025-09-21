import os
import logging
import aiohttp
import asyncio
import base64
from typing import List, Optional
from email.mime.text import MIMEText
from livekit.agents import function_tool, RunContext
from langchain_community.tools import DuckDuckGoSearchRun
from google_auth_helper import get_access_token


# -------------------------
# Weather Tool
# -------------------------
@function_tool()
async def get_weather(context: RunContext, city: str) -> str:
    """
    Fetch current weather for a given city using OpenWeather API.
    """
    try:
        api_key = os.getenv("OPENWEATHER_API_KEY")
        if not api_key:
            return "Weather API key missing in .env"

        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return f"Failed to fetch weather for {city}."
                data = await resp.json()
                desc = data["weather"][0]["description"]
                temp = data["main"]["temp"]
                return f"Weather in {city}: {desc}, {temp}°C"
    except Exception as e:
        logging.error(f"get_weather error: {e}")
        return f"Error fetching weather for {city}"


# -------------------------
# Web Search Tool
# -------------------------
@function_tool()
async def search_web(context: RunContext, query: str) -> str:
    """
    Perform a web search using DuckDuckGo.
    """
    try:
        results = await asyncio.to_thread(DuckDuckGoSearchRun().run, query)
        return results
    except Exception as e:
        logging.error(f"search_web error: {e}")
        return f"Error searching the web for '{query}'"


# -------------------------
# Gmail Tool
# -------------------------
@function_tool()
async def send_email(
    context: RunContext,
    to_email: str,
    subject: str,
    message: str,
    cc_email: Optional[List[str]] = None
) -> str:
    """
    Send an email using Gmail API.
    """
    try:
        access_token = get_access_token()
        if not access_token:
            return "Google access token unavailable."

        mime_msg = MIMEText(message)
        mime_msg["to"] = to_email
        mime_msg["subject"] = subject
        if cc_email:
            mime_msg["cc"] = ", ".join(cc_email)

        raw_msg = base64.urlsafe_b64encode(mime_msg.as_bytes()).decode()

        url = "https://gmail.googleapis.com/gmail/v1/users/me/messages/send"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        payload = {"raw": raw_msg}

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as resp:
                if resp.status in [200, 201]:
                    return f"Email sent to {to_email}"
                else:
                    text = await resp.text()
                    logging.error(f"Gmail API error: {text}")
                    return f"Failed to send email: {text}"

    except Exception as e:
        logging.error(f"send_email error: {e}")
        return f"Error sending email: {e}"


# -------------------------
# Google Calendar Tools
# -------------------------
@function_tool()
async def create_calendar_event(
    context: RunContext,
    summary: str,
    start_time: str,
    end_time: str,
    attendees: Optional[List[str]] = None,
    description: str = ""
) -> str:
    """
    Create a new Google Calendar event.
    """
    try:
        access_token = get_access_token()
        if not access_token:
            return "Google access token unavailable."

        event = {
            "summary": summary,
            "description": description,
            "start": {"dateTime": start_time, "timeZone": "Asia/Kolkata"},
            "end": {"dateTime": end_time, "timeZone": "Asia/Kolkata"},
        }
        if attendees:
            event["attendees"] = [{"email": email} for email in attendees]

        url = "https://www.googleapis.com/calendar/v3/calendars/primary/events"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=event) as resp:
                if resp.status in [200, 201]:
                    data = await resp.json()
                    return f"Event created: {data.get('htmlLink','No link')}"
                else:
                    text = await resp.text()
                    logging.error(f"Calendar API error: {text}")
                    return f"Failed to create event: {text}"

    except Exception as e:
        logging.error(f"create_calendar_event error: {e}")
        return f"Error creating calendar event: {e}"


@function_tool()
async def list_upcoming_events(context: RunContext, max_results: int = 5) -> str:
    """
    List upcoming events from the primary Google Calendar.
    """
    try:
        access_token = get_access_token()
        if not access_token:
            return "Google access token unavailable."

        import datetime
        now = datetime.datetime.utcnow().isoformat() + "Z"
        url = (
            "https://www.googleapis.com/calendar/v3/calendars/primary/events"
            f"?maxResults={max_results}&timeMin={now}&singleEvents=true&orderBy=startTime"
        )
        headers = {"Authorization": f"Bearer {access_token}"}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    events = data.get("items", [])
                    if not events:
                        return "No upcoming events found."
                    response = ""
                    for ev in events:
                         start = ev["start"].get("dateTime", ev["start"].get("date"))
                         response += f"- {ev['summary']} at {start} (ID: {ev['id']})\n"
                    return response.strip()
                else:
                    text = await resp.text()
                    logging.error(f"Calendar API error: {text}")
                    return f"Failed to list events: {text}"

    except Exception as e:
        logging.error(f"list_upcoming_events error: {e}")
        return f"Error fetching events: {e}"

@function_tool()
async def delete_calendar_event(context: RunContext, event_id: str) -> str:
    """
    Delete an event from the primary Google Calendar by event ID.
    """
    try:
        access_token = get_access_token()
        if not access_token:
            return "Google access token unavailable."

        url = f"https://www.googleapis.com/calendar/v3/calendars/primary/events/{event_id}"
        headers = {"Authorization": f"Bearer {access_token}"}

        async with aiohttp.ClientSession() as session:
            async with session.delete(url, headers=headers) as resp:
                if resp.status == 204:  # 204 = No Content (successful deletion)
                    return f"Event {event_id} deleted successfully."
                else:
                    text = await resp.text()
                    logging.error(f"Calendar API error: {text}")
                    return f"Failed to delete event {event_id}: {text}"

    except Exception as e:
        logging.error(f"delete_calendar_event error: {e}")
        return f"Error deleting event: {e}"
@function_tool()
async def delete_event_by_name(context: RunContext, event_name: str) -> str:
    """
    Delete a Google Calendar event by its name (summary).
    If multiple matches are found, returns them for clarification.
    """
    try:
        access_token = get_access_token()
        if not access_token:
            return "Google access token unavailable."

        import datetime
        now = datetime.datetime.utcnow().isoformat() + "Z"
        url = (
            "https://www.googleapis.com/calendar/v3/calendars/primary/events"
            f"?timeMin={now}&singleEvents=true&orderBy=startTime"
        )
        headers = {"Authorization": f"Bearer {access_token}"}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    logging.error(f"Calendar API error: {text}")
                    return f"Failed to search events: {text}"
                
                data = await resp.json()
                events = data.get("items", [])
                matches = [ev for ev in events if event_name.lower() in ev["summary"].lower()]

                if not matches:
                    return f"No events found with name containing '{event_name}'."

                if len(matches) > 1:
                    response = "Multiple events match:\n"
                    for ev in matches:
                        start = ev["start"].get("dateTime", ev["start"].get("date"))
                        response += f"- {ev['summary']} at {start} (ID: {ev['id']})\n"
                    response += "Please specify the ID of the event to delete."
                    return response

                # Only one match → delete directly
                event_id = matches[0]["id"]
                delete_url = f"https://www.googleapis.com/calendar/v3/calendars/primary/events/{event_id}"
                async with session.delete(delete_url, headers=headers) as delete_resp:
                    if delete_resp.status == 204:
                        return f"Event '{matches[0]['summary']}' deleted successfully."
                    else:
                        text = await delete_resp.text()
                        logging.error(f"Calendar delete error: {text}")
                        return f"Failed to delete event: {text}"

    except Exception as e:
        logging.error(f"delete_event_by_name error: {e}")
        return f"Error deleting event by name: {e}"
