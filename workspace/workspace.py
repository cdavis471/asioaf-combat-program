##################################
######  Joe's Duel Re‐work  ######
#####  Test Code for Maesty  #####
##################################

import random

# ----------------------------- Data Classes -----------------------------
class Character:
    """Represents a combatant with base stats, perks, and dynamic combat state."""
    def __init__(self, name, speed, attack, defense, morale=50, age=30, perks=None, combat_type="melee"):
        # Base stats
        self.name = name
        self.base_speed = speed
        self.base_attack = attack
        self.base_defense = defense
        self.base_morale = morale
        self.age = age
        self.perks = perks or []
        self.combat_type = combat_type
        # Dynamic combat stats (set in initialize_character)
        self.current_speed = speed
        self.current_attack = attack
        self.current_defense = defense
        self.current_morale = morale
        # Injury/malus tracking
        self.injuries_sustained = 0
        self.major_injuries_ignored = 0     # how many Major Injury maluses can be ignored (Indomitable)
        # Perk state trackers
        self.used_ff_reroll = False         # Favored by Fortune (T1) one-time reroll used
        self.used_ff_opp_reroll = False     # Favored by Fortune (T2) opponent crit reroll used
        self.berserker_triggered = False    # Berserker (T1) buff applied
        self.berserker_rampage_rounds = 0   # Berserker (T2) extra rounds fighting after 0 HP

# ------------------------- Injury Tables -------------------------
PRIMARY_INJURY_TABLE = {
    "blunted": [(1,20,"Major Injury"), (21,100,"Minor Injury")],
    "live":    [(1,25,"Death"), (26,40,"Critical Injury"),
                (41,71,"Major Injury"), (72,100,"Minor Injury")]
}
SECONDARY_INJURY_TABLE = {
    "blunted": [(1,20,"Major Injury"), (21,100,"Minor Injury")],
    "live":    [(1,2,"Critical Injury"), (3,40,"Major Injury"), (41,100,"Minor Injury")]
}
CRITICAL_INJURIES = {
    1:  ("Death","Killed outright"),
    # Entries 2–19 would detail specific critical injuries in a full implementation
    20: ("Knocked Unconscious","No lasting malus, but combatant is knocked out")
}

# ------------------------- Dice Rolls -------------------------
def roll_d20():
    return random.randint(1, 20)
def roll_2d20():
    d1, d2 = roll_d20(), roll_d20()
    return d1+d2, d1, d2
def roll_3d5():
    return random.randint(1,5) + random.randint(1,5) + random.randint(1,5)
def roll_d100():
    return random.randint(1, 100)
def roll_d3():
    return random.randint(1, 3)

# ------------------------- Injury Resolution -------------------------
def resolve_injury_roll(table, weapon_type="live"):
    r = roll_d100()
    for low, high, result in table[weapon_type]:
        if low <= r <= high:
            return result
def resolve_critical_injury():
    r = roll_d20()
    return CRITICAL_INJURIES.get(r, ("Critical Injury", "Severe injury"))

# ------------------------- Perk & Age Initialization -------------------------
def apply_age_malus(char):
    """Apply age-based stat maluses (reduced by Duelist perks)."""
    age = char.age
    malus = 0
    if age <= 15:
        malus = min(16-age, 5) * 2
    elif 51 <= age <= 60:
        malus = 2
    elif 61 <= age <= 70:
        malus = 4
    elif 71 <= age <= 80:
        malus = 6
    elif 81 <= age <= 90:
        malus = 8
    elif age >= 91:
        malus = 10
    # Duelist reduces age malus (2 per tier)
    for t in (3,2,1):
        if f"Duelist T{t}" in char.perks:
            malus = max(0, malus - 2*t)
            break
    # Reduce base stats by malus (not below 0)
    char.base_speed   = char.base_speed - malus
    char.base_attack  = char.base_attack - malus
    char.base_defense = char.base_defense - malus

def apply_initial_perks(char, duel_type):
    """Adjust base stats according to perks (weapon specialists, etc.) and set special counters."""
    # Indomitable: set base morale and Major Injury ignore count
    if "Indomitable T3" in char.perks:
        char.base_morale = 95  # +15 morale
    elif "Indomitable T2" in char.perks:
        char.base_morale = 80  # +15 morale
    elif "Indomitable T1" in char.perks:
        char.base_morale = 65  # +15 morale
    # Determine how many major injury maluses can be ignored (highest tier of Indomitable)
    for t in (3,2,1):
        if f"Indomitable T{t}" in char.perks:
            char.major_injuries_ignored = t
            break
    # Context for specialist perks (use combat_type for 'mixed')
    context = duel_type if duel_type in ("melee","ranged") else char.combat_type
    # Apply stat bonuses from all perks
    for perk in char.perks:
        if "Blade Specialist" in perk and context == "melee":
            tier = int(perk[-1])
            if tier == 1: 
                char.base_speed += 1; char.base_attack += 1; char.base_defense += 0
            elif tier == 2: 
                char.base_speed += 2; char.base_attack += 1; char.base_defense += 1
            elif tier == 3: 
                char.base_speed += 2; char.base_attack += 2; char.base_defense += 2
        if "Axe and Blunt Specialist" in perk and context == "melee":
            tier = int(perk[-1])
            if tier == 1: 
                char.base_speed += 1; char.base_attack += 1; char.base_defense += 0
            elif tier == 2: 
                char.base_speed += 2; char.base_attack += 2; char.base_defense += 0
            elif tier == 3: 
                char.base_speed += 2; char.base_attack += 3; char.base_defense += 1
        if "Spear Specialist" in perk and context == "melee":
            tier = int(perk[-1])
            if tier == 1: 
                char.base_speed += 1; char.base_attack += 0; char.base_defense += 1
            elif tier == 2: 
                char.base_speed += 2; char.base_attack += 1; char.base_defense += 1
            elif tier == 3: 
                char.base_speed += 3; char.base_attack += 1; char.base_defense += 2
        if "Duelist" in perk and context == "melee":
            tier = int(perk[-1])
            if tier == 1: 
                char.base_speed += 2; char.base_attack += 0; char.base_defense += 0
            elif tier == 2: 
                char.base_speed += 4; char.base_attack += 0; char.base_defense += 0
            elif tier == 3: 
                char.base_speed += 6; char.base_attack += 0; char.base_defense += 0
        if "Shield Specialist" in perk:
            tier = int(perk[-1])
            # Melee: +2 Defense each tier; Ranged: +1 Defense each tier
            if context == "melee":
                if tier == 1: 
                    char.base_speed += 0; char.base_attack += 0; char.base_defense += 2
                elif tier == 2: 
                    char.base_speed += 0; char.base_attack += 0; char.base_defense += 4
                elif tier == 3: 
                    char.base_speed += 0; char.base_attack += 0; char.base_defense += 6
            else:
                if tier == 1: 
                    char.base_speed += 0; char.base_attack += 0; char.base_defense += 1
                elif tier == 2: 
                    char.base_speed += 0; char.base_attack += 0; char.base_defense += 2
                elif tier == 3: 
                    char.base_speed += 0; char.base_attack += 0; char.base_defense += 3
        if "Bow Specialist" in perk and context == "ranged":
            tier = int(perk[-1])
            if tier == 1: 
                char.base_speed += 2; char.base_attack += 1; char.base_defense += 0
            elif tier == 2: 
                char.base_speed += 3; char.base_attack += 2; char.base_defense += 0
            elif tier == 3: 
                char.base_speed += 4; char.base_attack += 3; char.base_defense += 0
        if "Crossbow Specialist" in perk and context == "ranged":
            tier = int(perk[-1])
            if tier == 1: 
                char.base_speed += 1; char.base_attack += 2; char.base_defense += 0
            elif tier == 2: 
                char.base_speed += 2; char.base_attack += 4; char.base_defense += 0
            elif tier == 3: 
                char.base_speed += 3; char.base_attack += 6; char.base_defense += 0
        if "Marksman" in perk and context == "ranged":
            tier = int(perk[-1])
            if tier == 1: 
                char.base_speed += 2; char.base_attack += 0; char.base_defense += 0
            elif tier == 2: 
                char.base_speed += 4; char.base_attack += 0; char.base_defense += 0
            elif tier == 3: 
                char.base_speed += 6; char.base_attack += 1; char.base_defense += 0
        if "Battlefield Champion" in perk:
            # All duels: +1 Speed, +1 Attack (Defense remains as base)
            if tier == 1: 
                char.base_speed += 1; char.base_attack += 1; char.base_defense += 0
            elif tier == 2: 
                char.base_speed += 2; char.base_attack += 2; char.base_defense += 0
            elif tier == 3: 
                char.base_speed += 3; char.base_attack += 3; char.base_defense += 0
        if "Steel Tempest" in perk and context == "melee":
            # Melee duels: +1 Attack, +1 Defense (all tiers)
            if tier == 1: 
                char.base_speed += 0; char.base_attack += 1; char.base_defense += 1
            elif tier == 2: 
                char.base_speed += 0; char.base_attack += 2; char.base_defense += 2
            elif tier == 3: 
                char.base_speed += 0; char.base_attack += 3; char.base_defense += 3
        if "Sworn Sword" in perk and context == "melee":
            # Melee duels: +1 Speed, +1 Defense (all tiers)
            if tier == 1: 
                char.base_speed += 1; char.base_attack += 0; char.base_defense += 1
            elif tier == 2: 
                char.base_speed += 2; char.base_attack += 0; char.base_defense += 2
            elif tier == 3: 
                char.base_speed += 3; char.base_attack += 0; char.base_defense += 3
        if "Thrown Projectile Specialist" in perk:
            tier = int(perk[-1]) if perk[-1].isdigit() else 1
            # All tiers: +1 Speed; Tier 3: +1 Attack as well
            if tier == 1: 
                char.base_speed += 1; char.base_attack += 0; char.base_defense += 0
            elif tier == 2: 
                char.base_speed += 2; char.base_attack += 0; char.base_defense += 0
            elif tier == 3: 
                char.base_speed += 3; char.base_attack += 1; char.base_defense += 0
        # (Other battlefield/duel-seeking perks affect out-of-duel behavior or require context beyond this simulation.)

def initialize_character(char, duel_type):
    """Apply age and perk modifiers to set current stats at duel start."""
    apply_initial_perks(char, duel_type)
    apply_age_malus(char)
    char.current_speed = char.base_speed
    char.current_attack = char.base_attack
    char.current_defense = char.base_defense
    char.current_morale = char.base_morale

# ------------------------- Perk-Aware Roll and Attack Helpers -------------------------
def roll_initiative(char):
    """Roll 2d20 for initiative, add Speed, with Favored by Fortune (T1) rerolling any one '1' once."""
    total, d1, d2 = roll_2d20()
    total += char.current_speed
    # Favored by Fortune T1: one-time reroll if any die came up 1
    if "Favored by Fortune" in char.perks and not char.used_ff_reroll:
        if d1 == 1 or d2 == 1:
            char.used_ff_reroll = True
            if d1 < d2:
                new = roll_d20(); total += new - d1; d1 = new
            else:
                new = roll_d20(); total += new - d2; d2 = new
    return total, d1, d2

def roll_attack(attacker, defender, is_ranged=False):
    """Roll the attack (3d5 + Attack - Defense, minimum 1) and subtract from defender's morale."""
    raw = roll_3d5() + attacker.current_attack - defender.current_defense
    dmg = max(raw, 1)
    defender.current_morale -= dmg
    return dmg

def apply_secondary_injury(char, weapon_type="live"):
    """Roll on the secondary injury table and apply any conditional perk effects (Berserker T1)."""
    result = resolve_injury_roll(SECONDARY_INJURY_TABLE, weapon_type)
    # Berserker T1: first time character suffers a Minor Injury, gain +2 Attack and +2 Speed
    if result == "Minor Injury" and any(p.startswith("Berserker") for p in char.perks) and not char.berserker_triggered:
        char.berserker_triggered = True
        char.current_speed += 2
        char.current_attack += 2
    return result

def apply_primary_injury(char, weapon_type="live"):
    """Roll on the primary injury table (used when a character is defeated)."""
    return resolve_injury_roll(PRIMARY_INJURY_TABLE, weapon_type)

# ------------------------------ Combat Initialization ------------------------------
def prepare_duel(team1, team2, duel_type):
    """Initialize all characters on both teams for the duel."""
    for char in team1:
        initialize_character(char, duel_type)
    for char in team2:
        initialize_character(char, duel_type)

# ------------------------------ Combat Simulations ------------------------------
def single_combat_melee_melee(team1, team2, duel_type="melee"):
    """Simulate a one-on-one melee duel."""
    log = []
    c1, c2 = team1[0], team2[0]
    rnd = 1
    while True:
        # Initiative rolls
        i1, d11, d12 = roll_initiative(c1)
        i2, d21, d22 = roll_initiative(c2)
        log.append(f"Round {rnd}: {c1.name} rolls {d11}+{d12}+Spd{c1.current_speed}={i1}")
        log.append(f"Round {rnd}: {c2.name} rolls {d21}+{d22}+Spd{c2.current_speed}={i2}")
        if i1 == i2:
            log.append("Tie – no attack.")
            rnd += 1
            continue
        # Determine attacker and defender based on higher initiative
        if i1 > i2:
            atk, defn = c1, c2
            dice = (d11, d12)
        else:
            atk, defn = c2, c1
            dice = (d21, d22)
        # Check for crit (20 or Duelist T3's 19) and fail (1)
        has20 = (20 in dice) or (19 in dice and "Duelist T3" in atk.perks)
        has1 = (1 in dice)
        # Favored by Fortune T2: force a reroll if defender's opponent rolled a crit
        if has20 and not has1 and "Favored by Fortune T2" in defn.perks and not defn.used_ff_opp_reroll:
            defn.used_ff_opp_reroll = True
            log.append("→ Favored by Fortune T2 triggers a re-roll!")
            # Skip applying this round's attack; go back to initiative roll
            continue
        # Resolve critical strike or failure effects (no double-count if both 20 and 1)
        if not (has20 and has1):
            if has20:
                # Critical Strike: secondary injury and stat malus to defender
                sec = apply_secondary_injury(defn)
                malus = 2  # base malus for a crit strike
                if sec == "Minor Injury":
                    # Ageing With Grace: ignore minor injury malus
                    if "Ageing With Grace" in defn.perks:
                        malus = 0
                elif sec == "Major Injury":
                    if "Indomitable" in " ".join(defn.perks) and defn.major_injuries_ignored > 0:
                        malus = 0
                        defn.major_injuries_ignored -= 1
                    elif "Ageing With Grace" in defn.perks:
                        malus = 1  # half malus
                    else:
                        malus = 2
                # Favored by Fortune T2 passive: halve the crit malus (to min 1)
                if "Favored by Fortune T2" in defn.perks and malus >= 2:
                    malus = max(1, malus // 2)
                if malus > 0:
                    # Reduce defender's highest stat by malus
                    key_stat = max(("current_speed","current_attack","current_defense"), key=lambda s: getattr(defn, s))
                    setattr(defn, key_stat, getattr(defn, key_stat) - malus)
                    stat_name = key_stat[len("current_"):].capitalize()
                    log.append(f"→ Crit Strike! {defn.name}'s {stat_name} -{malus}; SecInj: {sec}")
                else:
                    log.append(f"→ Crit Strike! {defn.name} ignores the injury malus; SecInj: {sec}")
            elif has1:
                # Critical Failure: secondary injury and stat malus to attacker
                sec = apply_secondary_injury(atk)
                malus = 2  # base malus for a crit fail
                if sec == "Minor Injury":
                    if "Ageing With Grace" in atk.perks:
                        malus = 0
                elif sec == "Major Injury":
                    if "Indomitable" in " ".join(atk.perks) and atk.major_injuries_ignored > 0:
                        malus = 0
                        atk.major_injuries_ignored -= 1
                    elif "Ageing With Grace" in atk.perks:
                        malus = 1
                    else:
                        malus = 2
                # (Favored by Fortune T2 does not affect self-inflicted failures)
                if malus > 0:
                    key_stat = max(("current_speed","current_attack","current_defense"), key=lambda s: getattr(atk, s))
                    setattr(atk, key_stat, getattr(atk, key_stat) - malus)
                    stat_name = key_stat[len("current_"):].capitalize()
                    log.append(f"→ Crit Fail! {atk.name}'s {stat_name} -{malus}; SecInj: {sec}")
                else:
                    log.append(f"→ Crit Fail! {atk.name} ignores the injury malus; SecInj: {sec}")
        # Attack roll and damage application
        dmg = roll_attack(atk, defn)
        # Steel Tempest T3: double damage on crit strikes
        if "Steel Tempest T3" in atk.perks and has20 and not has1:
            defn.current_morale -= dmg  # apply damage again
            dmg *= 2
        log.append(f"{atk.name} hits {defn.name} for {dmg} (Morale {defn.current_morale})")
        # Check if defender is defeated
        if defn.current_morale <= 0:
            # Berserker T2: upon hitting 0, fight on for 1-3 more rounds
            if "Berserker T2" in defn.perks and defn.berserker_rampage_rounds == 0:
                defn.berserker_rampage_rounds = roll_d3()
                defn.current_morale = 1  # keep them alive
                log.append(f"{defn.name} enters a berserker rage for {defn.berserker_rampage_rounds} more rounds!")
                rnd += 1
                continue  # continue the duel instead of ending it
            # Defender is actually defeated – determine primary injury and winner
            prim = apply_primary_injury(defn)
            log.append(f"{defn.name} defeated! PrimInj: {prim}")
            log.append(f"{atk.name} wins!")
            return log
        # Decrement Berserker T2 extra rounds and handle expiry (for each combatant)
        for combatant, opponent in ((c1, c2), (c2, c1)):
            if combatant.berserker_rampage_rounds:
                combatant.berserker_rampage_rounds -= 1
                if combatant.berserker_rampage_rounds == 0 and combatant.current_morale > 0 and opponent.current_morale > 0:
                    # Berserker's extra time expired without ending duel -> they collapse (forfeit)
                    crit_injury = resolve_critical_injury()
                    log.append(f"{combatant.name} collapses from exhaustion! CriticalInj: {crit_injury[0]}")
                    log.append(f"{opponent.name} wins!")
                    return log
        rnd += 1

def single_combat_ranged_melee(team1, team2, duel_type="mixed"):
    """Simulate a one-on-one duel where one side is ranged and the other melee."""
    log = []
    rng = team1[0]  # ranged combatant
    m = team2[0]    # melee combatant
    # Phase 1: Ranged volleys (2 rounds normally, 3 rounds if Marksman T3)
    volley_rounds = 3 if "Marksman T3" in rng.perks else 2
    for rnd in range(1, volley_rounds+1):
        i, d1, d2 = roll_initiative(rng)
        log.append(f"Round {rnd}: {rng.name} rolls {d1}+{d2}+Spd{rng.current_speed}={i}")
        if i >= 30:
            dmg = roll_attack(rng, m, is_ranged=True)
            log.append(f"{rng.name} fires {m.name} for {dmg} (Morale {m.current_morale})")
            if m.current_morale <= 0:
                prim = apply_primary_injury(m)
                log.append(f"{m.name} defeated! PrimInj: {prim}")
                log.append(f"{rng.name} wins!")
                return log
        else:
            log.append(f"{rng.name} fails to hit (needs 30).")
    # If melee character has Thrown Specialist T2/T3, they get a counter-throw at end of last volley
    if any(p.startswith("Thrown Projectile Specialist T2") or p.startswith("Thrown Projectile Specialist T3") for p in m.perks):
        i_th, d1_th, d2_th = roll_initiative(m)
        log.append(f"Round {volley_rounds}: {m.name} makes a thrown attack (initiative {i_th})")
        if i_th >= 30:
            dmg_th = roll_attack(m, rng, is_ranged=True)
            log.append(f"{m.name} hits {rng.name} with a thrown weapon for {dmg_th} (Morale {rng.current_morale})")
            if rng.current_morale <= 0:
                prim = apply_primary_injury(rng)
                log.append(f"{rng.name} defeated! PrimInj: {prim}")
                log.append(f"{m.name} wins!")
                return log
        else:
            log.append(f"{m.name}'s thrown attack misses (needs 30).")
    # Phase 2: Melee engagement
    melee_round = volley_rounds + 1
    dmg = roll_attack(m, rng)
    log.append(f"Round {melee_round}: {m.name} strikes {rng.name} for {dmg} (Morale {rng.current_morale})")
    if rng.current_morale <= 0:
        prim = apply_primary_injury(rng)
        log.append(f"{rng.name} defeated! PrimInj: {prim}")
        log.append(f"{m.name} wins!")
        return log
    log.append(f"Switching to melee from round {melee_round+1}+")
    # Continue melee from next round until someone wins
    # We reuse single_combat_melee_melee for the continued fight (skipping its initialization and Round 1 log)
    continued_log = single_combat_melee_melee([m], [rng], duel_type="melee")
    # The first entry of continued_log will be "Round 1: ..." for the continued duel, which is actually Round melee_round+1 overall
    # We adjust round numbering in logging for continuity:
    for entry in continued_log:
        if entry.startswith("Round "):
            # Replace "Round 1" with "Round X" where X = melee_round+1
            round_num = int(entry.split(":")[0].split()[1]) + melee_round
            log.append(entry.replace(f"Round 1:", f"Round {round_num}:"))
        else:
            log.append(entry)
    return log

def single_combat_ranged_ranged(team1, team2, duel_type="ranged"):
    """Simulate a one-on-one ranged duel."""
    log = []
    a1, a2 = team1[0], team2[0]
    rnd = 1
    while True:
        i1, d11, d12 = roll_initiative(a1)
        i2, d21, d22 = roll_initiative(a2)
        log.append(f"Round {rnd}: {a1.name} rolls {d11}+{d12}+Spd{a1.current_speed}={i1}")
        log.append(f"Round {rnd}: {a2.name} rolls {d21}+{d22}+Spd{a2.current_speed}={i2}")
        s1 = (i1 >= 30)
        s2 = (i2 >= 30)
        if s1:
            dmg = roll_attack(a1, a2, is_ranged=True)
            log.append(f"{a1.name} fires {a2.name} for {dmg} (Morale {a2.current_morale})")
            if a2.current_morale <= 0:
                prim = apply_primary_injury(a2)
                log.append(f"{a2.name} defeated! PrimInj: {prim}")
                log.append(f"{a1.name} wins!")
                return log
        if s2:
            dmg = roll_attack(a2, a1, is_ranged=True)
            log.append(f"{a2.name} fires {a1.name} for {dmg} (Morale {a1.current_morale})")
            if a1.current_morale <= 0:
                prim = apply_primary_injury(a1)
                log.append(f"{a1.name} defeated! PrimInj: {prim}")
                log.append(f"{a2.name} wins!")
                return log
        if not s1 and not s2:
            log.append("No one reached 30—no attack.")
        rnd += 1

def multi_combat_melee_melee(team1, team2, duel_type="melee"):
    """Simulate a multi-combat melee duel (teams of multiple combatants)."""
    log = []
    combatants = []
    # Initialize all combatants
    for side, team in enumerate((team1, team2), start=1):
        for c in team:
            combatants.append({'char': c, 'side': side, 'init': 0})
    rnd = 1
    while True:
        alive = [entry for entry in combatants if entry['char'].current_morale > 0]
        if len({entry['side'] for entry in alive}) < 2:
            # One side has no one left standing
            if alive:
                log.append(f"Side {alive[0]['side']} wins!")
            else:
                log.append("All combatants are down!")
            break
        log.append(f"--- Round {rnd} Initiatives ---")
        for entry in alive:
            i, _, _ = roll_initiative(entry['char'])
            entry['init'] = i
            log.append(f"{entry['char'].name}(S{entry['side']}) i={i}")
        # Sort by initiative descending for action order
        alive.sort(key=lambda x: -x['init'])
        # Track if an IP T2 character has been attacked already this round
        attacked_set = set()
        for entry in alive:
            atk = entry['char']
            targets = [t for t in alive 
                       if t['side'] != entry['side'] and t['init'] < entry['init'] and t['char'].current_morale > 0]
            if not targets:
                continue
            defn_entry = min(targets, key=lambda x: x['init'])
            defn = defn_entry['char']
            # If defender has IP T2 and was already attacked this round, skip further attacks on them
            if defn in attacked_set and any(p.startswith("Imposing Presence T2") for p in defn.perks):
                log.append(f"{atk.name} cannot strike {defn.name} this round (Imposing Presence).")
                continue
            dmg = roll_attack(atk, defn)
            log.append(f"{atk.name} hits {defn.name} for {dmg} (Mor {defn.current_morale})")
            # Fear the Old Man: extra secondary injury if attacker is outnumbered by >=4
            if any(p.startswith("Fear the Old Man") for p in atk.perks):
                allies_alive = [x for x in alive if x['side'] == entry['side'] and x['char'].current_morale > 0]
                enemies_alive = [x for x in alive if x['side'] != entry['side'] and x['char'].current_morale > 0]
                if len(enemies_alive) - len(allies_alive) >= 4 and defn.current_morale > 0:
                    sec = apply_secondary_injury(defn)
                    log.append(f"→ {atk.name}'s attack triggers extra injury: {sec}")
            # Check if defender is down
            if defn.current_morale <= 0:
                # Imposing Presence threshold: if defender is alone and above their extended threshold, keep them alive
                if any(p.startswith("Imposing Presence") for p in defn.perks):
                    # Check if defn has any allies still alive
                    allies_alive = [x for x in alive if x['side'] == defn_entry['side'] and x['char'] != defn and x['char'].current_morale > 0]
                    if not allies_alive:
                        extra_thresh = 0
                        if "Imposing Presence T1" in defn.perks: 
                            extra_thresh += 10
                        if "Imposing Presence T2" in defn.perks: 
                            extra_thresh += 5
                        if defn.current_morale > -extra_thresh:
                            # Not past their defeat threshold – they stay up
                            defn.current_morale = 1
                            log.append(f"{defn.name} fights on despite injuries (Imposing Presence).")
                            # Mark that they were attacked this round (for IP T2 effect) 
                            attacked_set.add(defn)
                            continue  # skip logging defeat this iteration
                prim = apply_primary_injury(defn)
                log.append(f"{defn.name} defeated! PrimInj: {prim}")
            # Mark defender as attacked if they have IP T2 (to prevent multiple hits in the same round)
            if any(p.startswith("Imposing Presence T2") for p in defn.perks):
                attacked_set.add(defn)
        rnd += 1
    return log

def multi_combat_ranged_melee(team1, team2, duel_type="mixed"):
    """Simulate a multi-combat duel with one ranged team vs one melee team."""
    log = []
    # Phase 1: Ranged team gets 2 rounds of shooting
    for rnd in (1, 2):
        log.append(f"--- Ranged Round {rnd} ---")
        for shooter in list(team1):  # iterate over copy since we might remove from team2
            i, _, _ = roll_initiative(shooter)
            log.append(f"{shooter.name} rolls i={i}")
            if i >= 30 and team2:
                # Pick target with lowest morale on melee side
                target = min(team2, key=lambda c: c.current_morale)
                dmg = roll_attack(shooter, target, is_ranged=True)
                log.append(f"{shooter.name} fires {target.name} for {dmg} (Mor {target.current_morale})")
                if target.current_morale <= 0:
                    # Apply IP threshold: if target is last melee and above threshold, keep them alive
                    if any(p.startswith("Imposing Presence") for p in target.perks) and len(team2) == 1:
                        extra_thresh = 0
                        if "Imposing Presence T1" in target.perks: extra_thresh += 10
                        if "Imposing Presence T2" in target.perks: extra_thresh += 5
                        if target.current_morale > -extra_thresh:
                            target.current_morale = 1
                            log.append(f"{target.name} refuses to fall (Imposing Presence).")
                            continue
                    prim = apply_primary_injury(target)
                    log.append(f"{target.name} defeated! PrimInj: {prim}")
                    team2.remove(target)
            else:
                log.append(f"{shooter.name} fails to hit.")
        if not team2:
            log.append("Ranged side wins!")
            return log
    # Phase 2: Melee team gets a free round of attacks upon closing (Round 3)
    log.append("--- Melee Strike Round 3 ---")
    for striker in list(team2):
        i, _, _ = roll_initiative(striker)
        log.append(f"{striker.name} rolls i={i}")
        # Determine which ranged defenders the striker beats in initiative
        beaten = []
        for defender in list(team1):
            id_, _, _ = roll_initiative(defender)
            if i > id_:
                beaten.append(defender)
        if beaten:
            target = min(beaten, key=lambda c: c.current_morale)
            dmg = roll_attack(striker, target)
            log.append(f"{striker.name} hits {target.name} for {dmg} (Mor {target.current_morale})")
            if target.current_morale <= 0:
                if any(p.startswith("Imposing Presence") for p in target.perks) and len(team1) == 1:
                    extra_thresh = 0
                    if "Imposing Presence T1" in target.perks: extra_thresh += 10
                    if "Imposing Presence T2" in target.perks: extra_thresh += 5
                    if target.current_morale > -extra_thresh:
                        target.current_morale = 1
                        log.append(f"{target.name} fights on (Imposing Presence).")
                        continue
                prim = apply_primary_injury(target)
                log.append(f"{target.name} defeated! PrimInj: {prim}")
                team1.remove(target)
    if not team1:
        log.append("Melee side wins!")
        return log
    log.append("Switch to melee from round 4+")
    # Phase 3: Engage in full melee with remaining combatants
    post_log = multi_combat_melee_melee(team2, team1, duel_type="melee")
    log.extend(post_log)
    return log

def multi_combat_ranged_ranged(team1, team2, duel_type="ranged"):
    """Simulate a multi-combat duel where both sides are ranged."""
    log = []
    combatants = []
    for side, team in enumerate((team1, team2), start=1):
        for c in team:
            combatants.append({'char': c, 'side': side, 'init': 0})
    rnd = 1
    while True:
        alive = [entry for entry in combatants if entry['char'].current_morale > 0]
        if len({entry['side'] for entry in alive}) < 2:
            log.append(f"Side {alive[0]['side']} wins!")
            break
        log.append(f"--- Round {rnd} Initiatives ---")
        for entry in alive:
            i, _, _ = roll_initiative(entry['char'])
            entry['init'] = i
            log.append(f"{entry['char'].name}(S{entry['side']}) i={i}")
        alive.sort(key=lambda x: -x['init'])
        for entry in alive:
            atk = entry['char']
            if entry['init'] < 30:
                log.append(f"{atk.name} cannot fire.")
                continue
            targets = [t for t in alive 
                       if t['side'] != entry['side'] and t['init'] < entry['init'] and t['char'].current_morale > 0]
            if not targets:
                continue
            defn = min(targets, key=lambda x: x['init'])['char']
            dmg = roll_attack(atk, defn, is_ranged=True)
            log.append(f"{atk.name} fires {defn.name} for {dmg} (Mor {defn.current_morale})")
            if defn.current_morale <= 0:
                prim = apply_primary_injury(defn)
                log.append(f"{defn.name} defeated! PrimInj: {prim}")
        rnd += 1
    return log

# ------------------------------ Test Harness ------------------------------
# if __name__ == "__main__":
    # arya = Character("Arya Stark", 6, 4, 3, 50, 18, perks=["Berserker"], combat_type="melee")
    # hound = Character("Sandor Clegane", 4, 6, 5, 50, 36, perks=["Favored by Fortune"], combat_type="melee")
    # ygritte = Character("Ygritte", 5, 5, 2, 40, 25, perks=["Ageing With Grace"], combat_type="ranged")
    # jon = Character("Jon Snow", 5, 6, 3, 45, 25, perks=["Fear the Old Man"], combat_type="ranged")

    # Pick one scenario to test:
    # log = single_combat_melee_melee([arya],[hound], duel_type="melee")
    # log = single_combat_ranged_melee([ygritte],[arya], duel_type="mixed")
    # log = single_combat_ranged_ranged([jon],[ygritte], duel_type="ranged")
    # log = multi_combat_melee_melee([arya,Character("Brienne",3,5,6)], [hound,Character("Mountain",2,8,7)], duel_type="melee")
    # log = multi_combat_ranged_melee([ygritte],[arya, hound], duel_type="mixed")
    # log = multi_combat_ranged_ranged([jon, ygritte],[hound, Character("Tarly",4,4,3)], duel_type="ranged")

    # for line in log:
        # print(line)


# GUI Entry & Simulation Runner

def _get_combatant(idx, combat_type):
    print(f"\n=== Combatant #{idx} ({combat_type}) ===")
    name = input("Name: ").strip() or f"Fighter{idx}"
    # ask only for age and perks
    while True:
        try:
            age = int(input("Age: ").strip())
            break
        except ValueError:
            print("  → Please enter an integer for age.")
    perks_input = input(
        "Perks (comma-separated, e.g. 'Blade Specialist T3, Berserker'): "
    ).strip()
    perks = [p.strip() for p in perks_input.split(",") if p.strip()]

    # create with zero base stats—your perk & age logic will fill them in
    c = Character(name, 0, 0, 0, morale=50, age=age, perks=perks, combat_type=combat_type)
    # initialize_character(c, duel_type="mixed")
    return c


def display_stats(team1, team2, duel_type):
    """
    Print each combatant's initialized stats and perks.
    """
    print("\n=== Combatants Stats ===")
    for side, team in enumerate((team1, team2), start=1):
        for c in team:
            # ensure stats reflect current state
            # initialize_character(c, duel_type)
            perks_str = ", ".join(c.perks) if c.perks else "None"
            print(f"Side {side} - {c.name}: Age={c.age}, Speed={c.current_speed}, "
                  f"Attack={c.current_attack}, Defense={c.current_defense}, "
                  f"Morale={c.current_morale}, Perks=[{perks_str}]")


def _run_once(fn, team1, team2, duel_type):
    # display stats before running a single duel
    display_stats(team1, team2, duel_type)
    for line in fn(team1, team2, duel_type):
        print(line)


def _run_many(fn, team1, team2, duel_type, trials=10000):
    # display stats once before bulk simulations
    display_stats(team1, team2, duel_type)
    import copy
    wins = [0, 0]
    for _ in range(trials):
        # deep copy so we don't mutate the originals
        t1 = [copy.deepcopy(c) for c in team1]
        t2 = [copy.deepcopy(c) for c in team2]
        log = fn(t1, t2, duel_type)
        if log and "wins" in log[-1]:
            winner = log[-1].split(" wins")[0]
            if winner == team1[0].name:
                wins[0] += 1
            else:
                wins[1] += 1
    print(f"\nAfter {trials} runs:")
    print(f"  {team1[0].name} wins: {wins[0]}")
    print(f"  {team2[0].name} wins: {wins[1]}")


def main():
    scenarios = {
        "1": (single_combat_melee_melee,    "melee",        ("melee","melee")),
        "2": (single_combat_ranged_melee,   "mixed",        ("ranged","melee")),
        "3": (single_combat_ranged_ranged,  "ranged",       ("ranged","ranged")),
        "4": (multi_combat_melee_melee,     "melee_melee",  ("melee","melee")),
        "5": (multi_combat_ranged_melee,    "mixed",        ("ranged","melee")),
        "6": (multi_combat_ranged_ranged,   "ranged_ranged",("ranged","ranged")),
    }

    print("\n=== Main Menu ===")
    print("1. Single – Melee vs Melee")
    print("2. Single – Ranged vs Melee")
    print("3. Single – Ranged vs Ranged")
    print("4. Multi  – Melee vs Melee")
    print("5. Multi  – Ranged vs Melee")
    print("6. Multi  – Ranged vs Ranged")
    choice = input("Select scenario (1–6): ").strip()
    if choice not in scenarios:
        print("Invalid choice.")
        return
    fn, duel_type, (ct1, ct2) = scenarios[choice]

    print("\nMode:")
    print("1. Run Once")
    print("2. Run 10000 Runs & Win/Losses")
    mode = input("Select mode (1–2): ").strip()
    if mode not in ("1", "2"):
        print("Invalid mode.")
        return

    # build teams
    if choice in ("1", "2", "3"):
        c1 = _get_combatant(1, ct1)
        c2 = _get_combatant(2, ct2)
        team1, team2 = [c1], [c2]
    else:
        while True:
            try:
                n1 = int(input("\nTeam 1 size (1–25): ").strip())
                n2 = int(input("Team 2 size (1–25): ").strip())
                if 1 <= n1 <= 25 and 1 <= n2 <= 25:
                    break
            except ValueError:
                pass
            print("  → Please enter integers between 1 and 25.")
        team1 = [_get_combatant(i+1, ct1) for i in range(n1)]
        team2 = [_get_combatant(i+1, ct2) for i in range(n2)]

    # Initialize characters for the selected duel scenario
    prepare_duel(team1, team2, duel_type)   

    # execute
    if mode == "1":
        _run_once(fn, team1, team2, duel_type)
    else:
        _run_many(fn, team1, team2, duel_type, trials=10000)


if __name__ == "__main__":
    while True:
        main()
