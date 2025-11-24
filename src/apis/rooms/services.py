from sqlalchemy.orm import Session
import src.apis.rooms.models as models
import src.apis.rooms.schema as schemas
from fastapi import HTTPException
import math
import json
import httpx
import os
import asyncio


class RoomServices:
    def __init__(self):
        self.provider = os.getenv(
            "AI_PROVIDER", "groq")
        self.groq_api_key = os.getenv("GROQ_API_KEY")

        self.apis = {
            "groq": "https://api.groq.com/openai/v1/chat/completions",
        }

    def get_all_rooms(self, db: Session, skip: int = 0, limit: int = 20):
        total_query = db.query(models.Room)
        total = total_query.count()

        rooms_query = db.query(models.Room).offset(skip).limit(limit)
        rooms = rooms_query.all()

        page = (skip // limit) + 1 if limit > 0 else 1
        total_pages = math.ceil(total / limit) if limit > 0 else 1

        return {
            "data": rooms,
            "meta": {
                "page": page,
                "limit": limit,
                "total": total,
                "totalPage": total_pages
            }
        }

    def get_single_room(self, db: Session, room_id: str):
        return db.query(models.Room).filter(models.Room.id == room_id).first()

    def get_rooms_context(self, db: Session) -> str:
        """Get all rooms data to create context for AI"""
        try:
            rooms = db.query(models.Room).filter(
                models.Room.isDeleted == False).all()

            rooms_data = []
            for room in rooms:
                room_info = {
                    "id": str(room.id),
                    "name": getattr(room, 'name', 'N/A'),
                    "capacity": getattr(room, 'capacity', 'N/A'),
                    "pricePerSlot": getattr(room, 'price_per_slot', 'N/A'),
                    "amenities": getattr(room, 'amenities', []),
                    "description": getattr(room, 'description', 'N/A'),
                    "availability": getattr(room, 'is_available', True)
                }
                rooms_data.append(room_info)

            # IMPROVED: More natural and conversational system prompt
            context = f"""You are Sarah, a friendly and helpful room booking assistant. You work for a hotel/facility and genuinely care about helping guests find the perfect room.

PERSONALITY TRAITS:
- Always be warm, welcoming, and conversational
- Use natural language, not robotic responses
- Show genuine interest in helping customers
- Be enthusiastic but professional
- Use friendly expressions like "I'd be happy to help!", "Great choice!", "Perfect!"

CONVERSATION GUIDELINES:
- For greetings (hi, hello, hey): Respond warmly and offer help
- For thanks/gratitude: Say "You're welcome!" or "My pleasure!" naturally
- For goodbyes: Wish them well and invite them back
- Always sound human and personable
- Keep responses concise but warm

AVAILABLE ROOMS DATA:
{json.dumps(rooms_data, indent=2)}

Remember: You're helping real people find rooms they'll love. Be conversational, helpful, and genuinely friendly in every response."""

            return context

        except Exception as e:
            return """You are Sarah, a friendly room booking assistant. Be warm, conversational, and helpful. 
            Always respond naturally like you're talking to a friend, not like a computer."""

    async def chat_with_groq(self, message: str, context: str) -> str:
        """Chat using Groq (free tier: 10,000 requests/day)"""
        if not self.groq_api_key:
            return None

        headers = {
            "Authorization": f"Bearer {self.groq_api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "messages": [
                {"role": "system", "content": context},
                {"role": "user", "content": message}
            ],
            "model": "llama-3.1-8b-instant",
            "max_tokens": 200,  # Increased for more natural responses
            "temperature": 0.8,  # Increased for more creative/natural responses
            "top_p": 0.9,  # Added for more varied responses
            "frequency_penalty": 0.3,  # Reduces repetition
            "presence_penalty": 0.2  # Encourages more diverse vocabulary
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.apis["groq"],
                    headers=headers,
                    json=payload,
                    timeout=30.0
                )

                if response.status_code == 200:
                    result = response.json()
                    return result["choices"][0]["message"]["content"].strip()
                else:
                    return None

        except Exception as e:
            return None

    async def get_simple_response(self, message: str, db: Session) -> str:
        """IMPROVED: More natural fallback responses"""
        message_lower = message.lower()

        # Get rooms for context
        try:
            rooms = db.query(models.Room).filter(
                models.Room.isDeleted == False).all()
        except:
            rooms = []

        # IMPROVED: Natural greeting responses
        if any(word in message_lower for word in ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening']):
            greetings = [
                f"Hello there! 😊 I'm Sarah, your room booking assistant. We have {len(rooms)} fantastic rooms available. How can I help you find the perfect one today?",
                f"Hi! Great to meet you! I'm here to help you find an amazing room from our {len(rooms)} available options. What are you looking for?",
                f"Hey! Welcome! I'm Sarah and I'd love to help you book the perfect room. We have {len(rooms)} rooms ready for you. What can I help you with?"
            ]
            import random
            return random.choice(greetings)

        # IMPROVED: Natural thank you responses
        elif any(word in message_lower for word in ['thank', 'thanks', 'appreciate', 'grateful']):
            thanks_responses = [
                "You're so welcome! 😊 I'm always happy to help. Is there anything else you'd like to know about our rooms?",
                "My pleasure! That's what I'm here for. Feel free to ask if you need anything else!",
                "You're very welcome! I'm glad I could help. Don't hesitate to reach out if you have more questions!",
                "Aww, you're so sweet! Happy to help anytime. Anything else I can assist you with?"
            ]
            import random
            return random.choice(thanks_responses)

        # IMPROVED: Natural goodbye responses  
        elif any(word in message_lower for word in ['bye', 'goodbye', 'see you', 'later', 'farewell']):
            goodbye_responses = [
                "Goodbye! It was wonderful helping you today. Have a fantastic time, and feel free to come back anytime! 😊",
                "Take care! I hope you have an amazing stay. Don't hesitate to reach out if you need anything else!",
                "Bye for now! Thanks for letting me help you today. Have a wonderful day and enjoy your room!",
                "See you later! It was my pleasure assisting you. Have a great time! 👋"
            ]
            import random
            return random.choice(goodbye_responses)

        elif any(word in message_lower for word in ['book', 'reserve', 'availability']):
            return "I'd be happy to help you book a room! 😊 To find you the perfect match, could you tell me how many people you're booking for, your budget range, and any special amenities you'd love to have?"

        elif any(word in message_lower for word in ['capacity', 'size', 'people']):
            if rooms:
                capacities = [getattr(room, 'capacity', 'N/A')
                              for room in rooms]
                unique_capacities = sorted(
                    list(set([c for c in capacities if c != 'N/A' and isinstance(c, (int, float))])))
                if unique_capacities:
                    return f"Perfect question! We have rooms that can accommodate {', '.join(map(str, unique_capacities[:-1]))} and {unique_capacities[-1]} people. What size group are you planning for?"
            return "Great question! We have rooms of various sizes to fit different group needs. How many people will be staying?"

        elif any(word in message_lower for word in ['price', 'cost', 'rate', 'budget']):
            if rooms:
                prices = [getattr(room, 'price_per_slot', 'N/A')
                          for room in rooms]
                unique_prices = sorted(
                    list(set([p for p in prices if p != 'N/A' and isinstance(p, (int, float))])))
                if unique_prices:
                    return f"I'd love to help you find something in your budget! Our rooms range from ${min(unique_prices)} to ${max(unique_prices)} per slot. What price range works best for you?"
            return "I'd be happy to discuss pricing! We have options for different budgets. What range are you thinking?"

        elif any(word in message_lower for word in ['amenities', 'facilities', 'features']):
            if rooms:
                all_amenities = []
                for room in rooms:
                    amenities = getattr(room, 'amenities', [])
                    if isinstance(amenities, list):
                        all_amenities.extend(amenities)
                unique_amenities = list(set(all_amenities))
                if unique_amenities:
                    return f"Oh, you'll love our amenities! We offer {', '.join(unique_amenities[:-1])} and {unique_amenities[-1]}. Which of these sound most important to you?"
            return "We have some wonderful amenities available! What specific features are you hoping for in your room?"

        else:
            encouraging_responses = [
                f"I'm here and ready to help you find the perfect room! 😊 We have {len(rooms)} amazing options available. Feel free to ask me about pricing, capacity, amenities, or anything else you'd like to know!",
                f"Hey there! I'd love to help you discover the ideal room from our {len(rooms)} fantastic options. What would you like to know - pricing, room sizes, special features, or availability?",
                f"Welcome! I'm so excited to help you find an amazing room. With {len(rooms)} great choices available, I'm sure we'll find something perfect for you. What questions can I answer?"
            ]
            import random
            return random.choice(encouraging_responses)

    async def get_ai_response(self, message: str, db: Session) -> str:
        """Main method to get AI response - tries multiple cloud providers"""
        context = self.get_rooms_context(db)

        # List of providers to try in order (all Vercel-compatible)
        providers_to_try = [
            ("groq", self.chat_with_groq),
        ]

        # Try each provider
        for provider_name, chat_function in providers_to_try:
            try:
                response = await chat_function(message, context)
                print(provider_name)
                # Check if response is valid
                if response and len(response.strip()) > 0:
                    return response

            except Exception as e:
                print(f"Provider {provider_name} failed: {e}")
                continue

        # If all AI providers fail, use simple rule-based response
        return await self.get_simple_response(message, db)

    def create_room(self, db: Session, room: schemas.Room):
        room_data = room.model_dump(exclude_unset=True)
        new_room = models.Room(**room_data)
        db.add(new_room)
        db.commit()
        db.refresh(new_room)
        return room

    def update_room(self, db: Session, room_id: str, updated_data: schemas.RoomUpdate):
        room = self.get_single_room(db=db, room_id=room_id)

        if not room:
            raise HTTPException(status_code=404, detail="Room not found!!")

        updated_room_data = updated_data.model_dump(exclude_unset=True)

        for key, value in updated_room_data.items():
            if hasattr(room, key):
                setattr(room, key, value)

        try:
            db.commit()
            db.refresh(room)
            return room
        except Exception as e:
            raise HTTPException(
                status_code=400, detail=f"Error updating the room: {str(e)}")

    def delete_room(self, db: Session, room_id: str):
        room = self.get_single_room(db=db, room_id=room_id)

        if not room:
            raise HTTPException(status_code=404, detail="Room not found!!")

        room.isDeleted = True

        try:
            db.commit()
            db.refresh(room)
        except Exception as e:
            raise HTTPException(
                status_code=400, detail=f"Error deleting the room: {str(e)}")