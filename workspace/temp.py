####################################
########## CROWNED COMBAT ##########
####################################

import random
from typing import List, Optional

# Character Template
class Character:
    """Represents a duel participant with all attributes needed for combat."""
    BASE_MORALE = 50 # default base morale for all characters
    def __init__(self, name: str, age: int,
                 morale_threshold: int = 15,
                 injury_threshold: int = 4,
                 perks: Optional[List[str]] = None,
                 combat_type: str = "melee"):
        """
        Initialize a character. Base Speed, Attack, Defense start at 0 and are adjusted by perks and age.
        :param name: Character name.
        :param age: Character age (affects stat malus for very young or old fighters).
        :param morale_threshold: Morale threshold for yielding (default 15).
        :param injury_threshold: Injury count threshold for yielding (default 4).
        :param perks: List of perk names (e.g., ["Blade Specialist T2", "Indomitable T1"]).
        :param combat_type: "melee" or "ranged" to indicate their fighting style/weapon.
        """
        self.name = name    # character name
        self.age = age      # character age
        self.morale_threshold = morale_threshold    # morale threshold
        self.injury_threshold = injury_threshold    # injury threshold
        self.perks = perks[:] if perks else []  # for referencing issues
        self.combat_type = combat_type.lower()  # combat type
        if self.combat_type not in ("melee", "ranged"):
            raise ValueError("combat_type must be 'melee' or 'ranged'")

        # Base Combat Stats
        self.base_speed = 0
        self.base_attack = 0
        self.base_defense = 0
        self.base_morale = Character.BASE_MORALE

        # Dynamic Combat Stats
        self.current_speed = 0
        self.current_attack = 0
        self.current_defense = 0
        self.current_morale = 0

        # Injury / Perk States
        self.injuries_count = 0                 # total injuries sustained (minor or major)
        self.major_injuries_ignored = 0         # how many major injury penalties can be ignored (set by Indomitable)
        self.berserker_triggered = False        # whether Bloodlust (Berserker T1) has triggered the rage buff
        self.berserker_rampage_rounds = 0       # rounds remaining to fight after hitting 0 HP (Berserker T2)
        self.used_ff_reroll = False             # whether Born Lucky (Favored by Fortune T1) reroll was used
        self.used_ff_opp_reroll = False         # whether Favored by Fortune T2 opponent-crit reroll was used
        self.reroll_protection_used = False     # whether Shield Specialist T3 injury reroll was used in current round
        self.old_man_buff: bool = False         # starts inactive

    def apply_age_malus(self):
        """Apply age-based stat maluses, reduced by Duelist perks. This modifies base stats in-place."""
        malus = 0
        # Below 16
        if self.age <= 15:
            # Below 16 - Each year gives -2 (capped at -10 for below 12)
            malus = min(16 - self.age, 5) * 2
        # 51 - 60
        elif 51 <= self.age <= 60:
            malus = 2
        # 61 - 70
        elif 61 <= self.age <= 70:
            malus = 4
        # 71 - 80
        elif 71 <= self.age <= 80:
            malus = 6
        # 81 - 90
        elif 81 <= self.age <= 90:
            malus = 8
        # 91+
        elif self.age >= 91:
            malus = 10

        # Reduce malus by Duelist perks - Reduces age malus by 2 per tier - up to negating it entirely
        for tier in (3, 2, 1):  # check highest tier first
            if f"Duelist T{tier}" in self.perks:
                malus = max(0, malus - 2 * tier)
                break

       # Apply the malus to base stats ❶ — allow negatives
        if malus:
            self.base_speed   -= malus
            self.base_attack  -= malus
            self.base_defense -= malus
            
    def apply_perks(self, duel_type: str):
        """
        Apply all perk effects to adjust base stats and special counters before the duel.
        Also sets current stats = base stats.
        :param duel_type: "melee", "ranged", or "mixed" (for ranged vs melee scenarios). 
                          If "mixed", we use the character's own combat_type for context.
        """
        # If duel_type is not purely melee or purely ranged - use character's own type for applying perks
        context = duel_type if duel_type in ("melee", "ranged") else self.combat_type

        # Special-case perks that set base morale and injury ignore (Indomitable)
        if "Indomitable T3" in self.perks:
            self.base_morale = Character.BASE_MORALE + 15 * 3  # +45
        elif "Indomitable T2" in self.perks:
            self.base_morale = Character.BASE_MORALE + 15 * 2  # +30
        elif "Indomitable T1" in self.perks:
            self.base_morale = Character.BASE_MORALE + 15       # +15

        # Set how many Major Injury malus can be ignored (highest Indomitable tier)
        if "Indomitable T3" in self.perks:
            self.major_injuries_ignored = 3
        elif "Indomitable T2" in self.perks:
            self.major_injuries_ignored = 2
        elif "Indomitable T1" in self.perks:
            self.major_injuries_ignored = 1

        # Iterate through all perks and adjust stats accordingly
        for perk in self.perks:
            # Melee specialization perks
            if context == "melee":
                if perk.startswith("Blade Specialist T"):
                    tier = int(perk[-1])
                    # Blade Specialist: T1 (+1 Spd, +1 Atk), T2 (+2 Spd, +1 Atk, +1 Def), T3 (+2 Spd, +2 Atk, +2 Def)
                    if tier == 1:
                        self.base_speed += 1; self.base_attack += 1
                    elif tier == 2:
                        self.base_speed += 2; self.base_attack += 1; self.base_defense += 1
                    elif tier == 3:
                        self.base_speed += 2; self.base_attack += 2; self.base_defense += 2
                if perk.startswith("Axe and Blunt Specialist T"):
                    tier = int(perk[-1])
                    # Axe/Blunt: T1 (+1 Spd, +1 Atk), T2 (+2 Spd, +2 Atk), T3 (+2 Spd, +3 Atk, +1 Def)
                    if tier == 1:
                        self.base_speed += 1; self.base_attack += 1
                    elif tier == 2:
                        self.base_speed += 2; self.base_attack += 2
                    elif tier == 3:
                        self.base_speed += 2; self.base_attack += 3; self.base_defense += 1
                if perk.startswith("Spear Specialist T"):
                    tier = int(perk[-1])
                    # Spear: T1 (+1 Spd, +1 Def), T2 (+2 Spd, +1 Atk, +1 Def), T3 (+3 Spd, +1 Atk, +2 Def)
                    if tier == 1:
                        self.base_speed += 1; self.base_defense += 1
                    elif tier == 2:
                        self.base_speed += 2; self.base_attack += 1; self.base_defense += 1
                    elif tier == 3:
                        self.base_speed += 3; self.base_attack += 1; self.base_defense += 2
                if perk.startswith("Duelist T"):
                    tier = int(perk[-1])
                    # Duelist: primarily Speed. (v0.5: T1 +2 Spd, T2 +4 Spd, T3 +5 Spd)
                    if tier == 1:
                        self.base_speed += 2
                    elif tier == 2:
                        self.base_speed += 4
                    elif tier == 3:
                        self.base_speed += 5  # adjusted per v0.5 changelog (was +6 in earlier versions)
                if perk.startswith("Shield Specialist T"):
                    tier = int(perk[-1])
                    # Shield Specialist: Each tier gives +2 Defense in melee
                    self.base_defense += 2 * tier
                if perk.startswith("Steel Tempest T"):
                    tier = int(perk[-1])
                    # Steel Tempest: Each tier gives +1 Attack, +1 Defense in melee
                    self.base_attack += tier
                    self.base_defense += tier
                if perk.startswith("Sworn Sword T"):
                    tier = int(perk[-1])
                    # Sworn Sword: Each tier gives +1 Speed, +1 Defense in melee
                    self.base_speed += 1 * tier
                    self.base_defense += 1 * tier
                if perk == "Bloodlust":  # Berserker T1 renamed
                    # Bloodlust static effect: +2 Defense (the rage trigger is handled during combat)
                    self.base_defense += 2
                if perk == "Berserker":  # Berserker T2 renamed
                    # Berserker static effect: +2 Attack (the fight-after-0 effect handled in combat)
                    self.base_attack += 2
                if perk == "Fear the Old Man":
                    # No immediate stat change; effect is applied dynamically when outnumbered
                    pass

            # Ranged specialization perks
            if context == "ranged":
                if perk.startswith("Bow Specialist T"):
                    tier = int(perk[-1])
                    # Bow Specialist: T1 (+2 Spd, +1 Atk), T2 (+3 Spd, +2 Atk), T3 (+4 Spd, +3 Atk)
                    if tier == 1:
                        self.base_speed += 2; self.base_attack += 1
                    elif tier == 2:
                        self.base_speed += 3; self.base_attack += 2
                    elif tier == 3:
                        self.base_speed += 4; self.base_attack += 3
                if perk.startswith("Crossbow Specialist T"):
                    tier = int(perk[-1])
                    # Crossbow Specialist: T1 (+1 Spd, +2 Atk), T2 (+2 Spd, +4 Atk), T3 (+3 Spd, +6 Atk)
                    if tier == 1:
                        self.base_speed += 1; self.base_attack += 2
                    elif tier == 2:
                        self.base_speed += 2; self.base_attack += 4
                    elif tier == 3:
                        self.base_speed += 3; self.base_attack += 6
                if perk.startswith("Marksman T"):
                    tier = int(perk[-1])
                    # Marksman: T1 (+2 Spd), T2 (+4 Spd), T3 (+6 Spd, +1 Atk)
                    if tier == 1:
                        self.base_speed += 2
                    elif tier == 2:
                        self.base_speed += 4
                    elif tier == 3:
                        self.base_speed += 6; self.base_attack += 1
                    # (Battlefield duel seeking bonuses and sniping not applicable to direct duel simulation)
                # Shield Specialist in ranged context gives +1 Def per tier
                if perk.startswith("Shield Specialist T"):
                    tier = int(perk[-1])
                    self.base_defense += 1 * tier

            # Perks affecting all duel types (context doesn't matter)
            if perk.startswith("Thrown Projectile Specialist T"):
                tier = int(perk[-1])
                # Thrown Specialist: All duels +1 Speed per tier; T3 also +1 Attack
                self.base_speed += 1 * tier
                if tier == 3:
                    self.base_attack += 1  # Tier 3 thrown adds an attack as well
            if perk.startswith("Battlefield Champion T"):
                tier = int(perk[-1])
                # Battlefield Champion: +1 Speed, +1 Attack per tier (all duels)
                self.base_speed += 1 * tier
                self.base_attack += 1 * tier
            if perk.startswith("Favored by Fortune"):
                # Born Lucky / Favoured by Fortune
                if perk == "Favored by Fortune T1" or perk == "Born Lucky":
                    # PDF: +1 Speed, no Defence bonus  :contentReference[oaicite:0]{index=0}:contentReference[oaicite:1]{index=1}
                    self.base_speed += 1
                elif perk == "Favored by Fortune T2":
                    # PDF: +2 Defence  :contentReference[oaicite:2]{index=2}:contentReference[oaicite:3]{index=3}
                    self.base_defense += 2

        # Finalize current stats at start of duel
        self.apply_age_malus()  # apply age effects after applying perks to base stats
        self.current_speed   = self.base_speed
        self.current_attack  = self.base_attack
        self.current_defense = self.base_defense
        self.current_morale  = self.base_morale

    def take_damage(self, dmg: int):
        """Reduce morale by dmg (already calculated after subtracting defense)."""
        self.current_morale -= dmg
        if self.current_morale < 0:
            self.current_morale = int(self.current_morale)  # ensure it's an int (could be negative)

    def apply_malus(self, stat: str, amount: int):
        """Apply a permanent malus to one stat (Speed / Attack / Defense)."""
        if stat == "Speed":
            self.current_speed -= amount
        elif stat == "Attack":
            self.current_attack -= amount
        elif stat == "Defense":
            self.current_defense -= amount

    def apply_malus_to_all(self, amount: int) -> None:
        """Apply the same −amount penalty to Speed, Attack and Defense."""
        self.current_speed  -= amount
        self.current_attack -= amount
        self.current_defense-= amount

    def highest_stat(self) -> str:
        """Return which of Speed, Attack, Defense is currently highest (to apply crit malus)."""
        stats = {"Speed": self.current_speed, "Attack": self.current_attack, "Defense": self.current_defense}
        # Determine the highest value; if tied, we can choose Speed > Attack > Defense in that priority (or any consistent method)
        highest = max(stats, key=lambda k: (stats[k], k))  # use stat name as secondary key for consistency
        return highest

    def __repr__(self):
        return (f"<Character {self.name}: "
                f"Stats(S={self.current_speed}, A={self.current_attack}, D={self.current_defense}), "
                f"Morale={self.current_morale}>")

# --- Combat Simulation Logic ---

# Define injury tables (simplified for simulation purposes)
# The tables return an outcome category for a d100 roll.
PRIMARY_INJURY_TABLE = {
    "nonlethal": [  # e.g., blunted weapons or yielding duels
        (1, 10, "Major Injury"),   # 10% chance major injury
        (11, 30, "Minor Injury"),  # 20% chance minor injury
        (31, 100, "Minor Injury")  # remaining chance minor (in nonlethal we assume no death)
    ],
    "live": [       # lethal duel (using live steel)
        (1, 5, "Death"),          # 5% chance death outright
        (6, 20, "Critical Injury"), # 15% chance critical injury
        (21, 50, "Major Injury"),   # 30% major
        (51, 100, "Minor Injury")   # 50% minor
    ]
}
SECONDARY_INJURY_TABLE = [
    (1, 10, "Major Injury"),   # 10% chance major injury on secondary
    (11, 30, "Major Injury"),  # (perhaps a bit lower in reality, but for simulation we'll assume some chance)
    (31, 100, "Minor Injury")  # mostly minor injuries
]
CRITICAL_INJURY_TABLE = {
     1: ("Death",               lambda c: setattr(c, "current_morale", 0)),
     2: ("Brain Damage",        lambda c: c.apply_malus_to_all(12)),
     3: ("Spine Damage",        lambda c: c.apply_malus_to_all(12)),
     4: ("Internal Organ Hit",  lambda c: c.apply_malus_to_all(8)),
     5: ("Cracked Skull",       lambda c: c.apply_malus_to_all(8)),
     6: ("Punctured Lung",      lambda c: c.apply_malus_to_all(8)),
     7: ("Broken Arm",          lambda c: setattr(c, "current_attack",
                                                  max(0, c.current_attack - 8))),
     8: ("Broken Leg",          lambda c: setattr(c, "current_speed",
                                                  max(0, c.current_speed - 8))),
     9: ("Severed Hand",        lambda c: setattr(c, "current_attack",
                                                  max(0, c.current_attack - 10))),
    10: ("Severed Foot",        lambda c: setattr(c, "current_speed",
                                                  max(0, c.current_speed - 10))),
    11: ("Blinded Eye",         lambda c: c.apply_malus_to_all(6)),
    12: ("Deafened",            lambda c: c.apply_malus_to_all(4)),
    13: ("Pneumothorax",        lambda c: c.apply_malus_to_all(8)),   # TODO: 4-turn timer
    14: ("Severe Haemorrhage",  lambda c: c.apply_malus_to_all(8)),
    15: ("Broken Ribs",         lambda c: c.apply_malus_to_all(4)),
    16: ("Concussion",          lambda c: c.apply_malus_to_all(4)),
    17: ("Dislocated Shoulder", lambda c: setattr(c, "current_attack",
                                                  max(0, c.current_attack - 6))),
    18: ("Torn Tendon",         lambda c: c.apply_malus_to_all(6)),
    19: ("Deep Laceration",     lambda c: c.apply_malus_to_all(4)),
    20: ("Knocked Unconscious", lambda c: None),
}

def roll_d20():
    return random.randint(1, 20)

def roll_2d20():
    # Returns (total, die1, die2) for potential use in checking criticals
    d1 = roll_d20()
    d2 = roll_d20()
    return d1 + d2, d1, d2

def roll_3d5():
    # Roll 3 five-sided dice (3d5). We simulate a 5-sided die as randint 1-5.
    return random.randint(1, 5) + random.randint(1, 5) + random.randint(1, 5)

def roll_3d5_detail():
    """Return each die and the total for a 3d5 roll."""
    d1 = random.randint(1, 5)
    d2 = random.randint(1, 5)
    d3 = random.randint(1, 5)
    return (d1, d2, d3, d1 + d2 + d3)

def resolve_injury_roll(table, mode="nonlethal"):
    """
    Roll on an injury table. For primary injuries, mode can be 'nonlethal' or 'live' 
    to choose which table. For secondary injuries, provide a list of ranges.
    Returns the injury outcome string.
    """
    r = random.randint(1, 100)
    if isinstance(table, list):
        # Secondary table case (list of tuples)
        for low, high, result in table:
            if low <= r <= high:
                return result
    elif isinstance(table, dict):
        # Primary table case (dict with mode)
        for low, high, result in table[mode]:
            if low <= r <= high:
                return result
    return "Minor Injury"

def apply_critical_injury(victim: "Character", log: list) -> None:
    """Roll on CRITICAL_INJURY_TABLE and apply the effect."""
    roll = random.randint(1, 20)
    name, fn = CRITICAL_INJURY_TABLE[roll]
    fn(victim)
    victim.injuries_count += 1
    log.append(f"{victim.name} suffers a **Critical Injury – {name}!**")
    if name == "Death":
        victim.current_morale = 0

def switch_to_melee_context(char: "Character") -> None:
    """
    Convert a ranged combatant to melee stats after the volley phase.
    Removes ranged-specialist bonuses already baked into current_* and
    applies the equivalent melee-specialist bonuses. Injury penalties
    are left untouched.
    """
    # ── remove Bow / Crossbow / Marksman bonuses ──
    if "Bow Specialist T1" in char.perks:      char.current_speed -= 2; char.current_attack -= 1
    if "Bow Specialist T2" in char.perks:      char.current_speed -= 3; char.current_attack -= 2
    if "Bow Specialist T3" in char.perks:      char.current_speed -= 4; char.current_attack -= 3
    if "Crossbow Specialist T1" in char.perks: char.current_speed -= 1; char.current_attack -= 2
    if "Crossbow Specialist T2" in char.perks: char.current_speed -= 2; char.current_attack -= 4
    if "Crossbow Specialist T3" in char.perks: char.current_speed -= 3; char.current_attack -= 6
    if "Marksman T1" in char.perks:            char.current_speed -= 2
    if "Marksman T2" in char.perks:            char.current_speed -= 4
    if "Marksman T3" in char.perks:            char.current_speed -= 6; char.current_attack -= 1

    # ── add melee specialist bonuses (Blade shown; repeat for others) ──
    if "Blade Specialist T1" in char.perks:    char.current_speed += 1; char.current_attack += 1
    if "Blade Specialist T2" in char.perks:    char.current_speed += 2; char.current_attack += 1; char.current_defense += 1
    if "Blade Specialist T3" in char.perks:    char.current_speed += 2; char.current_attack += 2; char.current_defense += 2

    if "Axe and Blunt Specialist T1" in char.perks: char.current_speed += 1; char.current_attack += 1
    if "Axe and Blunt Specialist T2" in char.perks: char.current_speed += 2; char.current_attack += 2
    if "Axe and Blunt Specialist T3" in char.perks: char.current_speed += 2; char.current_attack += 3; char.current_defense += 1

    if "Spear Specialist T1" in char.perks:    char.current_speed += 1; char.current_defense += 1
    if "Spear Specialist T2" in char.perks:    char.current_speed += 2; char.current_attack += 1; char.current_defense += 1
    if "Spear Specialist T3" in char.perks:    char.current_speed += 3; char.current_attack += 1; char.current_defense += 2

    # Shield Specialist already gave +1 Def per tier in ranged – grant an extra +1 Def per tier in melee
    for perk in char.perks:
        if perk.startswith("Shield Specialist T"):
            tier = int(perk[-1])
            char.current_defense += tier

    char.combat_type = "melee"


def simulate_round(team_a: List[Character], team_b: List[Character], duel_type: str, round_num: int) -> str:
    """
    Simulate a single round of combat between two teams.
    Returns a log string describing actions this round.
    """
    log = []
    # All combatants roll initiative
    rolls = []  # list of tuples: (roll_total, d1, d2, character, team)
    for char in team_a + team_b:
        # Each character alive rolls initiative
        total, d1, d2 = roll_2d20()
        if (d1 == 1 or d2 == 1) and (
            "Born Lucky" in char.perks or "Favored by Fortune T1" in char.perks
        ) and not char.used_ff_reroll:
            char.used_ff_reroll = True
            total, d1, d2 = roll_2d20()        # fresh dice
        total += char.current_speed  # add Speed stat
        rolls.append((total, d1, d2, char))
        log.append(f"Round {round_num}: "
                   f"{char.name} rolls {d1} + {d2} + Spd{char.current_speed} = {total}")
    # Determine highest roll
    rolls.sort(key=lambda x: x[0], reverse=True)  # sort by total descending
    # Check for tie for highest
    if len(rolls) == 0:
        return ""  # no one to act
    highest_total = rolls[0][0] if rolls else 0
    tied = [entry for entry in rolls if entry[0] == highest_total]
    if len(tied) > 1:
        # Tie for top initiative: no attack this round
        log.append(f"Round {round_num}: **No clear initiative winner** (tie at {highest_total}). Both sides hesitate.")
        return "\n".join(log)

    # Otherwise, we have a clear winner
    total, d1, d2, attacker = rolls[0]
    # Determine defender team (target will be one from the opposite side)
    if attacker in team_a:
        opponent_team = team_b
    else:
        opponent_team = team_a

    # If opponent team is empty (shouldn't happen because duel would end), just return
    if not opponent_team:
        return ""

    # Critical checks for attacker (initiative winner) and defender (highest opponent)
    # We consider only attacker's dice for crit success, and also check if defender rolled a 1 for crit fail scenario.
    has20 = (d1 == 20 or d2 == 20)
    has1  = (d1 == 1 or d2 == 1)
    defender = random.choice(opponent_team)  # pick a random target from opposite side

    # Favored by Fortune T2: if attacker rolled a 20 and defender has FavFort T2 unused, force reroll of initiative
    if has20 and not has1 and "Favored by Fortune T2" in defender.perks and not defender.used_ff_opp_reroll:
        defender.used_ff_opp_reroll = True
        log.append(f"Round {round_num}: {defender.name}'s **Favored by Fortune T2** triggers! The opponent's critical initiative is nullified - rerolling the round.")
        # We signal to the outer simulation loop that we should redo this round by returning a special marker.
        return "RETRY"

    # Determine if critical strike or failure apply:
    # Critical Strike if any 20 and attacker actually won initiative
    critical_strike = False
    critical_failure = False
    if has20:
        # Attacker rolled a nat 20 on one die and has won init
        # (We already ensured they won since no tie)
        critical_strike = True
    if attacker in team_a:
        # Check the top opponent on team_b for nat1 on their roll (if they exist in rolls list)
        # Actually, simpler: if attacker has won, then anyone who lost with a nat1 would suffer crit fail.
        # We specifically check if the defender chosen had any nat1 in their roll.
        opp_roll = next((r for r in rolls if r[3] == defender), None)
        if opp_roll:
            _, od1, od2, _ = opp_roll
            if (od1 == 1 or od2 == 1):
                critical_failure = True
    else:
        # Attacker is in team_b, check defender (in team_a) for nat1
        opp_roll = next((r for r in rolls if r[3] == defender), None)
        if opp_roll:
            _, od1, od2, _ = opp_roll
            if (od1 == 1 or od2 == 1):
                critical_failure = True

    # However, critical failure should only apply if that person lost initiative. Here defender did lose.
    # So above is correct: if defender rolled a 1 on any die, it's a crit fail for them.

    # Log initiative result
    roll_desc = f"{attacker.name} (Initiative {total}"
    if has20 or has1:
        roll_desc += " ["
        if has20: roll_desc += "nat20!"
        if has20 and has1: roll_desc += " "
        if has1: roll_desc += "nat1!"
        roll_desc += "]"
    roll_desc += f") wins initiative and attacks {defender.name}."
    log.append(f"Round {round_num}: {roll_desc}")

    # Critical Strike effects
    if critical_strike:
        # Attacker landed a critical strike
        # Defender gets a -2 malus to their highest stat and must roll secondary injury.
        # Check Favored by Fortune T2 passive: if defender has it, halve malus (to -1)
        malus_amount = 2
        if "Favored by Fortune T2" in defender.perks:
            # But FavFort T2 does not protect against self-inflicted failures, only opponent's crits
            malus_amount = max(1, malus_amount // 2)
        # Apply malus to defender's highest stat
        key_stat = defender.highest_stat()
        defender.apply_malus(key_stat, malus_amount)
        log.append(f"**Critical Strike!** {defender.name} suffers –{malus_amount} {key_stat} and a secondary injury.")
        # Secondary injury roll for defender
        result = resolve_injury_roll(SECONDARY_INJURY_TABLE)
        # Shield Specialist T3 reroll if needed
        if result in ("Critical Injury", "Major Injury") and "Shield Specialist T3" in defender.perks and not defender.reroll_protection_used:
            defender.reroll_protection_used = True
            reroll_result = resolve_injury_roll(SECONDARY_INJURY_TABLE)
            result = reroll_result  # take the second result
            log.append(f"{defender.name}'s Shield Specialist T3 lets them **reroll** the injury; new result: **{result}**.")
        # Handle injury result
        if result == "Death":
            log.append(f"{defender.name} suffers a **fatal injury**!")
            defender.injuries_count += 1
            defender.current_morale = 0  # ensure they are down
        elif result == "Critical Injury":
            apply_critical_injury(defender, log)
        elif result == "Major Injury":
            log.append(f"{defender.name} suffers a **Major Injury**!")
            defender.injuries_count += 1
            # Major Injury imposes -1 to all stats, unless Indomitable can ignore
            if defender.major_injuries_ignored > 0:
                defender.major_injuries_ignored -= 1
                log.append(f"{defender.name} pushes through the pain (Indomitable perk negates stat penalty).")
            else:
                defender.current_speed   -= 2
                defender.current_attack  -= 2
                defender.current_defense -= 2
        elif result == "Minor Injury":
            log.append(f"{defender.name} suffers a **Minor Injury**.")
            defender.injuries_count += 1
            key = defender.highest_stat()
            defender.apply_malus(key, 1)
            # Minor injuries have no stat penalty
        # Berserker T1 (Bloodlust) trigger: if defender has not triggered and result is Minor Injury
        if result == "Minor Injury" and "Bloodlust" in defender.perks and not defender.berserker_triggered:
            defender.berserker_triggered = True
            defender.current_speed += 2
            defender.current_attack += 2
            log.append(f"{defender.name} enters a **Bloodlust** fury! (+2 Speed, +2 Attack)")

    # Critical Failure effects
    if critical_failure:
        # Defender (who lost initiative) rolled a nat1 on initiative -> critical failure
        # They suffer a -2 malus to highest stat and roll a secondary injury on themselves.
        malus_amount = 2
        if "Favored by Fortune T2" in defender.perks:
            # Favored by Fortune T2 does NOT help for self failures (explicitly noted in rules)
            malus_amount = 2  # no change
        key_stat = defender.highest_stat()
        defender.apply_malus(key_stat, malus_amount)
        log.append(f"**Critical Failure!** {defender.name} stumbles, suffering –{malus_amount} {key_stat} and a secondary injury.")
        result = resolve_injury_roll(SECONDARY_INJURY_TABLE)
        if result in ("Critical Injury", "Major Injury") and "Shield Specialist T3" in defender.perks and not defender.reroll_protection_used:
            defender.reroll_protection_used = True
            reroll_result = resolve_injury_roll(SECONDARY_INJURY_TABLE)
            result = reroll_result
            log.append(f"{defender.name}'s Shield Specialist T3 rerolls the injury; new result: **{result}**.")
        if result == "Death":
            log.append(f"{defender.name} suffers a **fatal self-injury**!")
            defender.injuries_count += 1
            defender.current_morale = 0
        elif result == "Critical Injury":
            apply_critical_injury(defender, log)
        elif result == "Major Injury":
            log.append(f"{defender.name} suffers a **Major Injury** from the mishap!")
            defender.injuries_count += 1
            if defender.major_injuries_ignored > 0:
                defender.major_injuries_ignored -= 1
                log.append(f"{defender.name}'s Indomitable grit negates the injury's stat penalty.")
            else:
                defender.current_speed   -= 2
                defender.current_attack  -= 2
                defender.current_defense -= 2
        elif result == "Minor Injury":
            log.append(f"{defender.name} suffers a **Minor Injury** from the mishap.")
            defender.injuries_count += 1
            key = defender.highest_stat()
            defender.apply_malus(key, 1)
        # Bloodlust check on defender for Berserker T1 as above
        if result == "Minor Injury" and "Bloodlust" in defender.perks and not defender.berserker_triggered:
            defender.berserker_triggered = True
            defender.current_speed += 2
            defender.current_attack += 2
            log.append(f"{defender.name} flies into a **Bloodlust** rage! (+2 Speed, +2 Attack)")

    # Perform the attack roll (if any attack occurs, i.e., initiative not tied)
    # We already chose 'attacker' and 'defender'. If either was removed due to a death injury from crit, skip attack.
    if attacker.current_morale <= 0 or defender.current_morale <= 0:
        # Someone died from a critical event before the attack could resolve.
        # We will end the round here.
        return "\n".join(log)
    # Calculate attack-roll damage (verbose version)
    ad1, ad2, ad3, dice_sum = roll_3d5_detail()                 # three individual d5
    raw_total = dice_sum + attacker.current_attack - defender.current_defense
    attack_roll = max(raw_total, 1)                            # cannot be less than 1
    defender.take_damage(attack_roll)

    log.append(f"{attacker.name} attack dice: {ad1}+{ad2}+{ad3}={dice_sum}  "
               f"+Atk{attacker.current_attack} −Def{defender.current_defense} "
               f"= {raw_total if raw_total>0 else 1} damage  "
               f"(morale ➞ {defender.current_morale})")


    # Berserker T2: if defender was reduced to 0 or below by this attack and defender has Berserker perk (T2)
    if defender.current_morale <= 0 and "Berserker" in defender.perks and defender.berserker_rampage_rounds == 0:
        # Trigger berserker rampage: get 1-3 extra rounds of fighting
        defender.berserker_rampage_rounds = random.randint(1, 3)
        log.append(f"{defender.name} enters a **Berserker rage** and fights on for {defender.berserker_rampage_rounds} more round(s) despite mortal wounds!")
        # Increase morale slightly above 0 to keep them "alive" during rage (could also just flag them as unkillable for rounds)
        defender.current_morale = 1

    # Check target's morale against threshold for yielding
    if defender.current_morale > 0 and defender.current_morale <= defender.morale_threshold:
        # Defender yields (forfeit)
        log.append(f"{defender.name} has reached morale threshold ({defender.current_morale} ≤ {defender.morale_threshold}) and **yields** the fight.")
        defender.current_morale = 0  # mark as out (0 or below means out)
    # Check target's injury threshold for yielding
    if defender.current_morale > 0 and defender.injuries_count >= defender.injury_threshold > 0:
        log.append(f"{defender.name} has suffered {defender.injuries_count} injuries (≥ {defender.injury_threshold}) and **can no longer continue**.")
        defender.current_morale = 0

    # After main attack, handle free attacks from extras if any (outnumbering)
    # Determine side numbers and contested capacity
    team_a_count = sum(1 for c in team_a if c.current_morale > 0)
    team_b_count = sum(1 for c in team_b if c.current_morale > 0)
    # Recalculate sides (because someone might have dropped to 0 in this attack)
    # If either side now has no fighters active, we skip free attacks as combat effectively ends.
    if team_a_count == 0 or team_b_count == 0:
        return "\n".join(log)
    if team_a_count and team_b_count:
        if team_a_count > team_b_count:
            larger_team = team_a; smaller_team = team_b
        elif team_b_count > team_a_count:
            larger_team = team_b; smaller_team = team_a
        else:
            larger_team: List[Character] = []      # not None → no Optional warnings
            smaller_team: List[Character] = []
        free_attacks = 0
        if larger_team:
            # Calculate contested capacity of smaller team
            contested_capacity = 0
            for char in smaller_team:
                base_capacity = 3
                # Adjust base capacity for Indomitable on that char
                if "Indomitable T3" in char.perks: 
                    base_capacity = 6
                elif "Indomitable T2" in char.perks:
                    base_capacity = 5
                elif "Indomitable T1" in char.perks:
                    base_capacity = 4
                contested_capacity += base_capacity
            # If larger side count exceeds contested capacity, determine number of free attacks
            larger_count = len(larger_team)
            smaller_count = len(smaller_team)
            if larger_count > contested_capacity:
                free_attacks = larger_count - contested_capacity
                if free_attacks < 0:
                    free_attacks = 0
            # Also, rule of >3:1 outnumbering: check ratio threshold 
            # (though contested_capacity approach covers it, we ensure >3:1 triggers at least 1)
            if larger_team and smaller_team:
                if larger_count > 3 * smaller_count:
                    # ensure at least 1 free attack
                    free_attacks = max(1, free_attacks)
        # Perform free attacks if any
        if free_attacks > 0:
            # Determine pool of attackers who have not acted yet from larger_team
            # If the attacker in this round was from the larger team, exclude them (they already attacked).
            free_attackers = [c for c in larger_team if c.current_morale > 0]
            if attacker in free_attackers:
                free_attackers.remove(attacker)
            # Limit free_attacks to number of available free attackers
            free_attacks = min(free_attacks, len(free_attackers))
            # Choose that many distinct attackers (random selection)
            random.shuffle(free_attackers)
            chosen_attackers = free_attackers[:free_attacks]
            for extra_attacker in chosen_attackers:
                if not smaller_team:
                    break  # no targets left
                extra_target = random.choice([c for c in smaller_team if c.current_morale > 0])
                # Free attack damage
                fd1, fd2, fd3, fsum = roll_3d5_detail()
                dmg = max(fsum + extra_attacker.current_attack - extra_target.current_defense, 1)
                log.append(f"[Free] {extra_attacker.name} dice {fd1}+{fd2}+{fd3}={fsum} "
                           f"+Atk{extra_attacker.current_attack} −Def{extra_target.current_defense} → {dmg}")
                if dmg < 1: 
                    dmg = 1
                extra_target.take_damage(dmg)
                log.append(f"**Free Attack:** {extra_attacker.name} hits {extra_target.name} for {dmg} damage! ({extra_target.current_morale} morale left)")
                # Check results of free attack on target
                if extra_target.current_morale <= 0:
                    # Target downed by free attack -> primary injury
                    log.append(f"{extra_target.name} is down to 0 morale from the free attack!")
                    # We roll primary injury (nonlethal assumption here)
                    outcome = resolve_injury_roll(PRIMARY_INJURY_TABLE, mode="nonlethal")
                    if outcome == "Death":
                        log.append(f"{extra_target.name} is **killed** in combat!")
                    elif outcome == "Critical Injury":
                        log.append(f"{extra_target.name} sustains a **Critical Injury**!")
                    elif outcome == "Major Injury":
                        log.append(f"{extra_target.name} sustains a **Major Injury** and is incapacitated!")
                    else:
                        log.append(f"{extra_target.name} is incapacitated with a **minor injury**.")
                    extra_target.injuries_count += 1
                    # We don't apply additional stat malus here because fight is basically over for them.
                elif extra_target.current_morale <= extra_target.morale_threshold and extra_target.current_morale > 0:
                    log.append(f"{extra_target.name} falls to morale {extra_target.current_morale} (≤ threshold) and **yields**.")
                    extra_target.current_morale = 0
                if extra_target.current_morale > 0 and extra_target.injuries_count >= extra_target.injury_threshold > 0:
                    log.append(f"{extra_target.name} has reached {extra_target.injuries_count} injuries (≥ threshold) and cannot continue.")
                    extra_target.current_morale = 0

    return "\n".join(log)

def simulate_duel(team_a: List[Character], team_b: List[Character],
                  duel_type: str = "melee", max_rounds: int = 100) -> str:
    """
    Simulate a duel between team A and team B.
    Supports 'melee', 'ranged', or 'mixed' (ranged vs melee) openings.
    """
    # ── apply static perk bonuses before combat ──
    if duel_type == "mixed":
        # Convention: team_a is the ranged side, team_b the melee side
        for c in team_a: c.apply_perks("ranged")
        for c in team_b: c.apply_perks("melee")
    else:
        for c in team_a + team_b: c.apply_perks(duel_type)

    log_lines: List[str] = []
    round_num = 1

    # ───────────────────────── volley phase (Fix # 6) ─────────────────────────
    if duel_type == "mixed":
        ranged_side = team_a
        melee_side  = team_b

        ranged_attackers = [c for c in ranged_side if c.current_morale > 0]
        melee_targets    = [c for c in melee_side  if c.current_morale > 0]

        if ranged_attackers and melee_targets:
            shooter = ranged_attackers[0]           # lead archer / crossbowman
            target  = melee_targets[0]              # lead melee fighter

            volley_rounds = 3 if "Marksman T3" in shooter.perks else 2

            for v in range(1, volley_rounds + 1):
                # Ranged shooter rolls uncontested vs 30
                r_total, sd1, sd2 = roll_2d20()
                r_total += shooter.current_speed

                # Melee fighter also rolls (for potential counter-throw)
                m_total, md1, md2 = roll_2d20()
                m_total += target.current_speed

                volley_desc = (
                    f"Volley {v}: {shooter.name} rolls "
                    f"{sd1}+{sd2}+Spd{shooter.current_speed} = {r_total}. "
                )

                if r_total >= 30:
                    dmg = max(roll_3d5() + shooter.current_attack - target.current_defense, 1)
                    target.take_damage(dmg)
                    volley_desc += (
                        f"**Hit** for {dmg} (morale {target.current_morale})."
                    )

                    # yield / death checks
                    if target.current_morale <= 0:
                        outcome = resolve_injury_roll(PRIMARY_INJURY_TABLE, mode="live")
                        volley_desc += f" {target.name} falls – {outcome}!"
                    elif target.current_morale <= target.morale_threshold:
                        volley_desc += f" {target.name} yields!"
                        target.current_morale = 0
                else:
                    volley_desc += "Misses the shot."

                # Counter-throw on the last volley for Thrown-Spec T2/T3
                if v == volley_rounds and (
                    "Thrown Projectile Specialist T2" in target.perks or
                    "Thrown Projectile Specialist T3" in target.perks
                ):
                    if m_total >= 30:
                        tdmg = max(
                            roll_3d5() + target.current_attack - shooter.current_defense,
                            1
                        )
                        shooter.take_damage(tdmg)
                        volley_desc += (
                            f"  {target.name} retaliates – hits for {tdmg} "
                            f"(morale {shooter.current_morale})."
                        )
                        if shooter.current_morale <= 0:
                            outcome = resolve_injury_roll(PRIMARY_INJURY_TABLE, mode="live")
                            volley_desc += f" {shooter.name} falls – {outcome}!"
                        elif shooter.current_morale <= shooter.morale_threshold:
                            volley_desc += f" {shooter.name} yields!"
                            shooter.current_morale = 0

                log_lines.append(volley_desc)

            # Free closing strike once melee reaches contact
            if melee_side and ranged_side and target.current_morale > 0 and shooter.current_morale > 0:
                d1, d2, d3, total_3d5 = roll_3d5_detail()
                dmg = max(total_3d5 + target.current_attack - shooter.current_defense, 1)
                shooter.take_damage(dmg)
                log_lines.append(
                    f"Closing-strike: {target.name} rolls {d1}+{d2}+{d3}={total_3d5}"
                    f" +Atk{target.current_attack} −Def{shooter.current_defense} → {dmg} "
                    f"(morale {shooter.current_morale})."
                )
                if shooter.current_morale <= 0:
                    outcome = resolve_injury_roll(PRIMARY_INJURY_TABLE, mode="live")
                    log_lines.append(f"{shooter.name} falls – {outcome}!")
                elif shooter.current_morale <= shooter.morale_threshold:
                    shooter.current_morale = 0
                    log_lines.append(f"{shooter.name} yields after the strike!")

            # Remove any combatants who yielded or died
            team_a = [c for c in team_a if c.current_morale > 0]
            team_b = [c for c in team_b if c.current_morale > 0]

            # Convert remaining ranged fighters to melee stats
            for fighter in ranged_side:
                switch_to_melee_context(fighter)

            duel_type = "melee"        # all further rounds are hand-to-hand

            # Early victory check
            if not team_a or not team_b:
                winner = "Side A" if team_a else "Side B"
                log_lines.append(f"**{winner} wins** after the volley phase!")
                return "\n".join(log_lines)

    # Main combat rounds
    while round_num <= max_rounds:
        # Reset Shield Specialist T3 reroll usage at start of each round
        for char in team_a + team_b:
            char.reroll_protection_used = False
        # Apply dynamic perk effects at round start (Fear the Old Man)
        count_a = sum(1 for c in team_a if c.current_morale > 0)
        count_b = sum(1 for c in team_b if c.current_morale > 0)
        for char in team_a:
            if "Fear the Old Man" in char.perks:
                # If outnumbered by 4 or more (enemy count >= char side count + 4)
                if count_b >= count_a + 4:
                    # Apply +3 all stats (if not already applied; we'll assume can stack or reapply fresh each time based on condition)
                    if not hasattr(char, 'old_man_buff') or not char.old_man_buff:
                        char.old_man_buff = True
                        char.current_speed += 3
                        char.current_attack += 3
                        char.current_defense += 3
                else:
                    # Remove buff if previously applied and condition no longer holds
                    if hasattr(char, 'old_man_buff') and char.old_man_buff:
                        char.old_man_buff = False
                        char.current_speed   -= 3
                        char.current_attack  -= 3
                        char.current_defense -= 3
        for char in team_b:
            if "Fear the Old Man" in char.perks:
                if count_a >= count_b + 4:
                    if not hasattr(char, 'old_man_buff') or not char.old_man_buff:
                        char.old_man_buff = True
                        char.current_speed += 3
                        char.current_attack += 3
                        char.current_defense += 3
                else:
                    if hasattr(char, 'old_man_buff') and char.old_man_buff:
                        char.old_man_buff = False
                        char.current_speed   -= 3
                        char.current_attack  -= 3
                        char.current_defense -= 3

        # Perform one round
        round_log = simulate_round(team_a, team_b, duel_type, round_num)
        if not round_log:
            # No action (e.g., if no characters, or other break condition)
            break
        if round_log.strip() == "RETRY":
            # Favored by Fortune T2 triggered a reroll of the round
            continue  # redo the same round number without incrementing
        log_lines.append(round_log)
        # Remove defeated characters (morale <= 0 means out)
        team_a = [c for c in team_a if c.current_morale > 0 or c.berserker_rampage_rounds > 0]
        team_b = [c for c in team_b if c.current_morale > 0 or c.berserker_rampage_rounds > 0]
        # Decrement berserker extra rounds and handle their expiration
        for combatant in team_a + team_b:
            if combatant.berserker_rampage_rounds:
                combatant.berserker_rampage_rounds -= 1
                if combatant.berserker_rampage_rounds == 0:
                    # Berserker time ended; if they're below 1 morale, they collapse now
                    if combatant.current_morale <= 0:
                        log_lines.append(f"{combatant.name}'s berserker rage ends and they finally collapse!")
                        # They are likely already removed next loop, but ensure morale is 0
                        combatant.current_morale = 0
        # Remove any who collapsed after berserker rage ended
        team_a = [c for c in team_a if c.current_morale > 0]
        team_b = [c for c in team_b if c.current_morale > 0]
        # Check victory condition
        if not team_a or not team_b:
            break
        round_num += 1

    # Determine outcome
    if team_a and not team_b:
        log_lines.append(f"**Side A wins!** {', '.join([c.name for c in team_a])} are victorious.\n")
    elif team_b and not team_a:
        log_lines.append(f"**Side B wins!** {', '.join([c.name for c in team_b])} are victorious.\n")
    else:
        log_lines.append("⚖️ The duel ends in a **draw** (max rounds reached or mutual defeat).\n")
    return "\n".join(log_lines)

def simulate_batch(team_a: List[Character], team_b: List[Character], duel_type: str = "melee", runs: int = 10000) -> str:
    """
    Simulate a batch of duels between team A and team B to gather statistics.
    Returns a summary of outcomes.
    """
    a_wins = 0
    b_wins = 0
    rounds_total = 0
    injuries_a = 0
    injuries_b = 0
    for i in range(runs):
        # Clone characters for each run (to avoid state carry-over)
        import copy
        sim_team_a = [copy.deepcopy(c) for c in team_a]
        sim_team_b = [copy.deepcopy(c) for c in team_b]
        # Re-apply initial perks and stats for each run
        if duel_type == "mixed":
            for char in sim_team_a:
                char.apply_perks("ranged")
            for char in sim_team_b:
                char.apply_perks("melee")
        else:
            for char in sim_team_a + sim_team_b:
                char.apply_perks(duel_type)
        # Simulate duel
        log = simulate_duel(sim_team_a, sim_team_b, duel_type=duel_type, max_rounds=1000)
        rounds = log.count("Round")
        rounds_total += rounds
        if "wins" in log:
            if "Side A wins" in log:
                a_wins += 1
            elif "Side B wins" in log:
                b_wins += 1
        # Count injuries (for simplicity, count total injury rolls from both sides)
        injuries_a += sum("injury" in line and any(name in line for name in [c.name for c in sim_team_a]) for line in log.splitlines())
        injuries_b += sum("injury" in line and any(name in line for name in [c.name for c in sim_team_b]) for line in log.splitlines())

    # Calculate and return statistics
    win_rate_a = a_wins / runs * 100
    win_rate_b = b_wins / runs * 100
    avg_rounds = rounds_total / runs
    avg_injuries_a = injuries_a / runs
    avg_injuries_b = injuries_b / runs
    summary = (f"Simulated {runs} duels:\n"
               f"- Side A wins: {a_wins} ({win_rate_a:.1f}%)\n"
               f"- Side B wins: {b_wins} ({win_rate_b:.1f}%)\n"
               # f"- Draws: {runs - a_wins - b_wins}\n"
               f"- Average rounds per duel: {avg_rounds:.2f}\n"
               f"- Average injuries per duel: Side A = {avg_injuries_a:.2f}, Side B = {avg_injuries_b:.2f}\n")
    return summary

# --- CLI Interface for user input ---
def main_cli():
    print("=== CROWNED COMBAT ===\n")
    # Choose combat type
    print("Choose Combat Type:")
    print("1. Melee vs Melee")
    print("2. Ranged vs Melee")
    print("3. Ranged vs Ranged\n")
    choice = input("Enter Choice (1-3): ").strip()
    if choice not in ("1", "2", "3"):
        print("\nInvalid Choice!\n")
        main_cli()
    if choice == "1":
        duel_type = "melee"
    elif choice == "2":
        duel_type = "mixed"
    else:
        duel_type = "ranged"

    # Number of combatants on each side
    try:
        num_a = int(input("\n# of Combatants - Side A: ").strip())
        num_b = int(input("# of Combatants - Side B: ").strip())
    except ValueError:
        print("Invalid number, defaulting to 1 vs 1.")
        num_a = 1
        num_b = 1

    # Initialize Teams
    team_a = []
    team_b = []

    # Helper: prompt for a character's details
    def get_character_input(idx, side):
        DEFAULT_MORALE_THRESHOLD = 15 # default base threshold for all characters
        print(f"\nEnter Details - {side} Combatant #{idx+1}:\n")
        name = input("Name: ")
        age = int(input("Age: "))
        mt_raw = input(f"Morale Threshold (default {DEFAULT_MORALE_THRESHOLD}): ").strip()
        mt = int(mt_raw) if mt_raw else DEFAULT_MORALE_THRESHOLD
        it = input("Injury Threshold (default 4): ")
        it = int(it) if it.strip() != "" else 4
        # List perks:
        print("Perks (comma-separated names, e.g. 'Blade Specialist T1, Duelist T2'):")
        perks_input = input("").strip()
        perks_list = [p.strip() for p in perks_input.split(",") if p.strip()] if perks_input else []
        # Determine combat_type for character (if mixed, side A is ranged, side B melee)
        c_type = "melee"
        if duel_type == "mixed":
            c_type = "ranged" if side == "Side A" else "melee"
        elif duel_type == "ranged":
            c_type = "ranged"
        # Create character
        char = Character(name, age, morale_threshold=mt, injury_threshold=it, perks=perks_list, combat_type=c_type)
        return char

    # Input characters for side A
    print("\n~~~ Side A Combatants ~~~")
    for i in range(num_a):
        char = get_character_input(i, "Side A")
        team_a.append(char)
    # Input characters for side B
    print("~~~ Side B Combatants ~~~")
    for j in range(num_b):
        char = get_character_input(j, "Side B")
        team_b.append(char)

    # Choose simulation mode (single or batch)
    print("~~~ Choose Simulation Mode ~~~\n")
    print("1. Single Duel - Detailed Log")
    print("2. Batch Duels - Detailed Stats (10K Iterations)\n")
    mode = input("Enter Choice (1 or 2): ").strip()
    if mode == "2":
        # Batch simulation
        # Apply initial perks to base stats for each char (without altering original input objects)
        for char in team_a + team_b:
            # We will deep-copy inside simulate_batch, so no need to apply now actually
            pass
        summary = simulate_batch(team_a, team_b, duel_type=duel_type, runs=10000)
        print("\n~~~ Batch Simulation Results ~~~\n")
        print(summary)
    else:
        # Single simulation
        result_log = simulate_duel(team_a, team_b, duel_type=duel_type)
        print("\n~~~ Duel Log ~~~\n")
        print(result_log)

# Entry point for CLI
if __name__ == "__main__":
    while True:
        main_cli()

# Example Google Sheets integration (pseudo-code, to be replaced with real API calls):
# sheet_data = fetch_sheet("DuelCharacters")  # Assume this returns a list of dicts or rows for each character
# for row in sheet_data:
#     char = Character(
#         name=row["Name"],
#         age=int(row["Age"]),
#         morale_threshold=int(row.get("MoraleThreshold", 15)),
#         injury_threshold=int(row.get("InjuryThreshold", 4)),
#         perks=[p.strip() for p in row["Perks"].split(",")] if row.get("Perks") else [],
#         combat_type=row.get("Type", "melee")
#     )
#     (team_a if row["Side"] == "A" else team_b).append(char)