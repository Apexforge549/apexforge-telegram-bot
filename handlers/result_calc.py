from database import db, users_collection
from datetime import datetime
from zoneinfo import ZoneInfo

transactions_collection = db["transactions"]
tournaments_collection = db["tournaments"]

IST = ZoneInfo("Asia/Kolkata")


async def process_tournament_result(tournament_id):

    # 🔥 Fetch tournament
    tournament = tournaments_collection.find_one({"tournament_id": tournament_id})

    if not tournament:
        return

    # 🔥 Prevent double processing
    if tournament.get("result_processed"):
        return
    # Fetching the winners from winners list in tournaments collection
    winners = tournament.get("winners", [])

    # ❗ No winners → skip
    if not winners:
        return

    # Separating the winner and the finalists
    winner = winners[0]
    finalists = winners[1:]
    
    prize_pool = tournament.get("prize_pool", 0)

    # 🔥 Prize calculation
    first_prize = int(prize_pool * 0.5)

    if finalists:
        finalist_prize_each = int((prize_pool * 0.5) / len(finalists))
    else:
        finalist_prize_each = 0

    # 🔥 Fetch all participants
    transactions = transactions_collection.find({
        "tournament_id": tournament_id,
        "type": "tournament_join"
    })

    for txn in transactions:

        username = txn.get("game_username")
        uid = txn.get("uid")

        # 🔥 Decide result + earning
        if username == winner:
            result = "winner"
            earning = first_prize

        elif username in finalists:
            result = "finalist"
            earning = finalist_prize_each

        else:
            result = "lose"
            earning = 0

        # 🔥 Update transaction
        transactions_collection.update_one(
            {"_id": txn["_id"]},
            {
                "$set": {
                    "result": result,
                    "earning": earning
                }
            }
        )

        # 🔥 Update user balance
        #if earning > 0:
            #users_collection.update_one(
                #{"uid": uid},                          # Active this when the withdraw button activates
                #{
                    #"$inc": {
                        #"winning_balance": earning,
                        #"balance": earning
                    #}
                #}
            #)
          
        # 🔥 UPDATE WINS (winner + finalists)
        if result in ["winner", "finalist"]:
            users_collection.update_one(
                {"uid": uid},
                {
                    "$inc": {
                        "wins": 1
                    }
                }
            )

    # 🔥 Mark as processed
    tournaments_collection.update_one(
        {"tournament_id": tournament_id},
        {
            "$set": {
                "result_processed": True,
                "completed_at": datetime.now(IST)
            }
        }
    )
