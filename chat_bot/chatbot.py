"""
QuickBite Bot - A rule-based FOOD ORDERING chatbot for a fictional
restaurant/food-delivery service called "QuickBite".

SPECIFIC USE CASE:
    A customer-facing chat assistant on QuickBite's ordering website/app.
    It lets a customer browse the menu, add items to a cart, check their
    cart, apply a discount code, place an order, track an active order,
    get delivery-time estimates, and cancel an order — all through natural
    language, while remembering the customer's name and cart contents for
    the duration of the chat session.

Run interactively:
    python chatbot.py

Author: Rutuja Khirsagar
"""

import re
import random


# ---------------------------------------------------------------------
# Restaurant menu (name -> price in INR)
# ---------------------------------------------------------------------
MENU = {
    "margherita pizza": 250,
    "veg burger": 120,
    "french fries": 90,
    "coke": 40,
    "pasta alfredo": 220,
    "garlic bread": 100,
    "chocolate brownie": 80,
}

# Valid promo codes -> % discount
PROMO_CODES = {
    "SAVE10": 10,
    "WELCOME15": 15,
    "QUICKBITE20": 20,
}


class QuickBiteBot:
    """Rule-based food-ordering chatbot for the QuickBite use case."""

    def __init__(self, bot_name="QuickBite Bot"):
        self.bot_name = bot_name
        self.context = {
            "user_name": None,
            "cart": {},              # item -> quantity
            "order_placed": False,
            "order_id": None,
            "eta_minutes": None,
            "discount_pct": 0,
            "last_intent": None,
            "turn_count": 0,
        }

    # ---------------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------------
    def _menu_text(self):
        lines = [f"- {name.title()}: ₹{price}" for name, price in MENU.items()]
        return "Here's our menu:\n" + "\n".join(lines)

    def _cart_total(self):
        return sum(MENU[item] * qty for item, qty in self.context["cart"].items())

    def _cart_text(self):
        cart = self.context["cart"]
        if not cart:
            return "Your cart is empty."
        lines = [f"- {qty} x {item.title()} (₹{MENU[item] * qty})" for item, qty in cart.items()]
        return "Your cart:\n" + "\n".join(lines) + f"\nSubtotal: ₹{self._cart_total()}"

    def extract_items(self, text):
        """Find (item, quantity) pairs mentioned in the message."""
        found = []
        for item in MENU:
            if re.search(r"\b" + re.escape(item) + r"\b", text):
                qty_match = re.search(r"(\d+)\s*(?:x\s*)?" + re.escape(item), text)
                qty = int(qty_match.group(1)) if qty_match else 1
                found.append((item, qty))
        return found

    def extract_promo_code(self, original_text):
        for code in PROMO_CODES:
            if code.lower() in original_text.lower():
                return code
        # catch an unrecognized code-like token, e.g. "apply code ABC123"
        match = re.search(r"\b([A-Z]{3,}\d{0,3})\b", original_text)
        return match.group(1) if match else None

    # ---------------------------------------------------------------
    # Intent detection + response (combined, since several intents
    # need to extract data from the message, not just classify it)
    # ---------------------------------------------------------------
    def respond(self, message):
        self.context["turn_count"] += 1
        text = message.lower().strip()

        # --- name capture ---
        name_match = re.search(r"\bmy name is (\w+)", text) or \
                     re.search(r"\bi am (\w+)\b", text) or \
                     re.search(r"\bi'm (\w+)\b", text) or \
                     re.search(r"^call me (\w+)", text)
        if name_match and not self.extract_items(text):
            name = name_match.group(1).capitalize()
            self.context["user_name"] = name
            self.context["last_intent"] = "give_name"
            return f"Nice to meet you, {name}! Want to see today's menu?"

        # --- cancel order ---
        if re.search(r"\bcancel\b.*\b(order|cart)\b|\bcancel my order\b", text):
            self.context["last_intent"] = "cancel_order"
            if self.context["order_placed"]:
                self.context["order_placed"] = False
                oid = self.context["order_id"]
                self.context["order_id"] = None
                return f"Order {oid} has been cancelled. Let me know if you'd like to order again."
            elif self.context["cart"]:
                self.context["cart"] = {}
                return "I've cleared your cart."
            else:
                return "You don't have an active order or cart to cancel."

        # --- track order ---
        if re.search(r"track (my )?order|where is my order|order status", text):
            self.context["last_intent"] = "track_order"
            if self.context["order_placed"]:
                return (f"Order {self.context['order_id']} is being prepared and should "
                        f"arrive in about {self.context['eta_minutes']} minutes.")
            return "You don't have an active order yet. Would you like to place one?"

        # --- delivery time / ETA ---
        if re.search(r"how long|delivery time|\beta\b|when will (it|my order) arrive", text):
            self.context["last_intent"] = "delivery_time"
            if self.context["order_placed"]:
                return f"Your order should arrive in about {self.context['eta_minutes']} minutes."
            return "Delivery usually takes 30-45 minutes once your order is placed."

        # --- apply discount code ---
        if re.search(r"\b(promo|discount|coupon)\b|\bapply code\b", text):
            self.context["last_intent"] = "apply_discount"
            code = self.extract_promo_code(message)
            if code and code.upper() in PROMO_CODES:
                self.context["discount_pct"] = PROMO_CODES[code.upper()]
                return f"Code {code.upper()} applied! You get {PROMO_CODES[code.upper()]}% off your order."
            return "That code doesn't look valid. Try SAVE10, WELCOME15, or QUICKBITE20."

        # --- checkout / place order ---
        if re.search(r"\bcheckout\b|place (my )?order|confirm order|that's all|i'm done ordering", text):
            self.context["last_intent"] = "checkout"
            if not self.context["cart"]:
                return "Your cart is empty — add something from the menu first!"
            subtotal = self._cart_total()
            discount = self.context["discount_pct"]
            total = round(subtotal * (1 - discount / 100))
            order_id = f"QB{random.randint(1000, 9999)}"
            eta = random.randint(25, 45)
            self.context.update({
                "order_placed": True,
                "order_id": order_id,
                "eta_minutes": eta,
                "cart": {},
                "discount_pct": 0,
            })
            discount_line = f" (after {discount}% off)" if discount else ""
            return (f"Order confirmed! Total: ₹{total}{discount_line}. "
                    f"Your order ID is {order_id}, arriving in ~{eta} minutes.")

        # --- view cart ---
        if re.search(r"my cart|what'?s in my (cart|order)\b|show (my )?cart", text):
            self.context["last_intent"] = "view_cart"
            return self._cart_text()

        # --- show menu ---
        if re.search(r"\bmenu\b|what do you have|what can i order|what('?s| is) available", text):
            self.context["last_intent"] = "show_menu"
            return self._menu_text()

        # --- add item(s) to order ---
        items = self.extract_items(text)
        if items:
            self.context["last_intent"] = "add_order"
            added_lines = []
            for item, qty in items:
                self.context["cart"][item] = self.context["cart"].get(item, 0) + qty
                added_lines.append(f"{qty} x {item.title()}")
            return (f"Added {', '.join(added_lines)} to your order. "
                    f"Current subtotal: ₹{self._cart_total()}. Anything else?")

        # --- greeting ---
        if re.search(r"\b(hi|hello|hey|good morning|good evening|good afternoon)\b", text):
            self.context["last_intent"] = "greeting"
            if self.context["user_name"]:
                return f"Hi again, {self.context['user_name']}! Ready to order?"
            return f"👋 Welcome to QuickBite! I'm {self.bot_name}. What's your name?"

        # --- ask bot identity ---
        if re.search(r"what('?s| is) your name|who are you", text):
            self.context["last_intent"] = "ask_bot_name"
            return f"I'm {self.bot_name}, here to help you order food from QuickBite."

        # --- thanks ---
        if re.search(r"\bthank(s| you)\b|\bthx\b", text):
            self.context["last_intent"] = "thanks"
            return "You're welcome! Enjoy your meal 🍽️"

        # --- help ---
        if re.search(r"\bhelp\b|what can you do|\boptions\b", text):
            self.context["last_intent"] = "help"
            return (
                "I can help you: view the menu, add items to your order, check your "
                "cart, apply a promo code, checkout, track your order, check delivery "
                "time, or cancel your order. Just tell me what you'd like!"
            )

        # --- goodbye ---
        if re.search(r"\b(bye|goodbye|see you|exit|quit|good night)\b", text):
            self.context["last_intent"] = "goodbye"
            name_part = f", {self.context['user_name']}" if self.context["user_name"] else ""
            return f"Thanks for visiting QuickBite{name_part}! Goodbye 👋"

        # --- fallback ---
        self.context["last_intent"] = "fallback"
        return self.fallback_response()

    def fallback_response(self):
        options = [
            "Sorry, I didn't get that. You can ask me for the menu, place an order, "
            "or check your order status.",
            "Hmm, I'm not sure what you mean. Try saying 'show menu' or 'I want a pizza'.",
            "I don't have an answer for that. I'm best at helping with food orders — "
            "want to see the menu?",
        ]
        return random.choice(options)

    # ---------------------------------------------------------------
    # Conversation loop
    # ---------------------------------------------------------------
    def greet(self):
        return (f"👋 Welcome to QuickBite! I'm {self.bot_name}. Type 'menu' to see what's "
                f"available, 'help' for options, or 'quit' to exit.")

    def run(self):
        print(self.greet())
        while True:
            try:
                user_input = input("You: ")
            except (EOFError, KeyboardInterrupt):
                print(f"\n{self.bot_name}: Goodbye!")
                break

            if not user_input.strip():
                print(f"{self.bot_name}: Please type something!")
                continue

            reply = self.respond(user_input)
            print(f"{self.bot_name}: {reply}")

            if self.context["last_intent"] == "goodbye":
                break


if __name__ == "__main__":
    bot = QuickBiteBot()
    bot.run()
