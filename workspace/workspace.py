######################################################################################################
################################### CROWNED DUELS - A MECH REWORK ####################################
######################################################################################################
# Created for /r/CrownedStag
# Contains framework for melee, mixed and ranged combat.
# Designed to work with /u/maesterbot
######################################################################################################

import random

######################################################################################################
# Character Class
######################################################################################################
class Character:
    """Crowned Stag Character Class"""
    def __init__(self, name, age=18, perks=None, injuries=None, injury_threshold=4, morale_threshold=15):

        # Base Stats
        self.name = name                            # Character Name
        self.age = age                              # Character Age
        self.perks = perks or []                    # Character Perks
        self.injuries = injuries or []              # Character Injuries
        self.injury_threshold = injury_threshold    # Injury Threshold
        self.morale_threshold = morale_threshold    # Morale Threshold

        # Dynamic Stats
        self.current_speed = 0                      # Current Speed
        self.current_attack = 0                     # Current Attack
        self.current_defense = 0                    # Current Defense
        self.current_morale = 50                    # Current Morale

        # Perk Check
        self.max_combatants = 3                     # Max Combatants Before Free Attack
        self.max_mixed_rounds = 2                   # Max Mixed Rounds (Ranged to Melee)
        self.major_injury_buff = 0                  # Indomitable Perk Check

        # Combat Checks
        self.currently_engaging = 0                 # Attacking Someone This Round
        self.crit_strike = 0                        # Crit Strike Rolled
        self.crit_fail = 0                          # Crit Fail Rolled
        self.combatants_faced = 0                   # Combatants Faced
        self.major_injuries = 0                     # Major Injuries Taken

######################################################################################################
# Stat Initialization
######################################################################################################
# Age Malus Function
def get_age_malus(age: int) -> int:
    """Set Age Malus For Character"""
    match age:                                      # Age
        case age if age >= 91:                      # -- 91
            return -10                              # --- Minus 10   
        
        case age if 81 <= age <= 90:                # -- 81-90
            return -8                               # --- Minus 8
        
        case age if 71 <= age <= 80:                # -- 71-80
            return -6                               # --- Minus 6
        
        case age if 61 <= age <= 70:                # -- 61-70
            return -4                               # --- Minus 4
        
        case age if 51 <= age <= 60:                # -- 51-60
            return -2                               # --- Minus 2
        
        case age if 16 <= age <= 50:                # -- 16-50
            return 0                                # --- No Malus
        
        case 15:                                    # -- 15
            return -2                               # --- Minus 2
        
        case 14:                                    # -- 14
            return -4                               # --- Minus 4
        
        case 13:                                    # -- 13
            return -6                               # --- Minus 6
        
        case 12:                                    # -- 12
            return -8                               # --- Minus 8
        
        case age if 0 <= age <= 11:                 # -- 0-11
            return -10                              # --- Minus 10
        
        case _:                                     # -- Else
            raise ValueError("Invalid age")         # -- Invalid Age

# Perk Stat Modifiers   
PERK_STAT_MODIFIERS = {

    # Blade Specialist Tree
    "Blade Specialist T1": {"melee": {"speed": 1, "attack": 1, "defense": 0}},                # Blade Specialist T1
    "Blade Specialist T2": {"melee": {"speed": 2, "attack": 1, "defense": 1}},                # Blade Specialist T2
    "Blade Specialist T3": {"melee": {"speed": 2, "attack": 2, "defense": 2}},                # Blade Specialist T3

    # Axe and Blunt Specialist Tree
    "Axe and Blunt Specialist T1": {"melee": {"speed": 1, "attack": 1, "defense": 0}},        # Axe and Blunt Specialist T1
    "Axe and Blunt Specialist T2": {"melee": {"speed": 2, "attack": 2, "defense": 0}},        # Axe and Blunt Specialist T2
    "Axe and Blunt Specialist T3": {"melee": {"speed": 2, "attack": 3, "defense": 1}},        # Axe and Blunt Specialist T3

    # Spear Specialist Tree
    "Spear Specialist T1": {"melee": {"speed": 1, "attack": 0, "defense": 1}},                # Spear Specialist T1
    "Spear Specialist T2": {"melee": {"speed": 2, "attack": 1, "defense": 1}},                # Spear Specialist T2
    "Spear Specialist T3": {"melee": {"speed": 3, "attack": 1, "defense": 2}},                # Spear Specialist T3

    # Duelist Tree
    "Duelist T1": {"melee": {"speed": 2, "attack": 0, "defense": 0}},                         # Duelist T1
    "Duelist T2": {"melee": {"speed": 4, "attack": 0, "defense": 0}},                         # Duelist T2
    "Duelist T3": {"melee": {"speed": 5, "attack": 0, "defense": 0}},                         # Duelist T3

    # Shield Specialist Tree
    "Shield Specialist T1": {"melee": {"speed": 0, "attack": 0, "defense": 2},                # Shield Specialist T1
                             "ranged": {"speed": 0, "attack": 0, "defense": 1}},
    "Shield Specialist T2": {"melee": {"speed": 0, "attack": 0, "defense": 4},                # Shield Specialist T2
                             "ranged": {"speed": 0, "attack": 0, "defense": 2}},
    "Shield Specialist T3": {"melee": {"speed": 0, "attack": 0, "defense": 6},                # Shield Specialist T3
                             "ranged": {"speed": 0, "attack": 0, "defense": 3}},

    # Steel Tempest Tree
    "Steel Tempest T1": {"melee": {"speed": 0, "attack": 1, "defense": 1}},                   # Steel Tempest T1
    "Steel Tempest T2": {"melee": {"speed": 0, "attack": 2, "defense": 2}},                   # Steel Tempest T2
    "Steel Tempest T3": {"melee": {"speed": 0, "attack": 3, "defense": 3}},                   # Steel Tempest T3

    # Sworn Sword Tree
    "Sworn Sword T1": {"melee": {"speed": 1, "attack": 0, "defense": 1}},                     # Sworn Sword T1
    "Sworn Sword T2": {"melee": {"speed": 2, "attack": 0, "defense": 2}},                     # Sworn Sword T2
    "Sworn Sword T3": {"melee": {"speed": 3, "attack": 0, "defense": 3}},                     # Sworn Sword T3

    # Battlefield Champion Tree
    "Battlefield Champion T1": {"all": {"speed": 1, "attack": 1, "defense": 0}},              # Battlefield Champion T1
    "Battlefield Champion T2": {"all": {"speed": 2, "attack": 2, "defense": 0}},              # Battlefield Champion T2
    "Battlefield Champion T3": {"all": {"speed": 3, "attack": 3, "defense": 0}},              # Battlefield Champion T3

    # Bow Specialist Tree
    "Bow Specialist T1": {"ranged": {"speed": 2, "attack": 1, "defense": 0}},                 # Bow Specialist T1
    "Bow Specialist T2": {"ranged": {"speed": 3, "attack": 2, "defense": 0}},                 # Bow Specialist T2
    "Bow Specialist T3": {"ranged": {"speed": 4, "attack": 3, "defense": 0}},                 # Bow Specialist T3

    # Crossbow Specialist Tree
    "Crossbow Specialist T1": {"ranged": {"speed": 1, "attack": 2, "defense": 0}},            # Crossbow Specialist T1
    "Crossbow Specialist T2": {"ranged": {"speed": 2, "attack": 4, "defense": 0}},            # Crossbow Specialist T2
    "Crossbow Specialist T3": {"ranged": {"speed": 3, "attack": 5, "defense": 0}},            # Crossbow Specialist T3

    # Marksman Tree
    "Marksman T1": {"ranged": {"speed": 2, "attack": 0, "defense": 0}},                       # Marksman T1
    "Marksman T2": {"ranged": {"speed": 4, "attack": 0, "defense": 0}},                       # Marksman T2
    "Marksman T3": {"ranged": {"speed": 6, "attack": 1, "defense": 0}},                       # Marksman T3

    # Projectile Specialist Tree
    "Thrown Projectile Specialist T1": {"all": {"speed": 1, "attack": 0, "defense": 0}},      # Thrown Projectile Specialist T1
    "Thrown Projectile Specialist T2": {"all": {"speed": 2, "attack": 0, "defense": 0}},      # Thrown Projectile Specialist T2
    "Thrown Projectile Specialist T3": {"all": {"speed": 3, "attack": 1, "defense": 0}},      # Thrown Projectile Specialist T3

    # Special Solo Prowess Perks
    "Bloodlust": {"melee": {"speed": 0, "attack": 0, "defense": 2}},                          # Bloodlust
    "Berserker": {"melee": {"speed": 0, "attack": 2, "defense": 0}},                          # Berserker
    "First in the Fray": {"all": {"speed": 1, "attack": 1, "defense": 1}},                    # First in the Fray
    "Born Lucky": {"all": {"speed": 1, "attack": 0, "defense": 2}},                           # Born Lucky
    "Favored by Fortune": {"all": {"speed": 1, "attack": 0, "defense": 2}}                    # Favored by Fortune

}

# Stat Initialization Functions - Melee
def melee_initialization(character):
    """Initialize Melee Stats for Character"""
    # Initialize Character Stats
    character.current_speed = 0                                                         # - Current Speed
    character.current_attack = 0                                                        # - Current Attack
    character.current_defense = 0                                                       # - Current Defense

    # Apply Age Malus
    age_malus = get_age_malus(character.age)                                            # - Get Age Malus
    character.current_speed += age_malus                                                # -- Apply Age Malus to Speed
    character.current_attack += age_malus                                               # -- Apply Age Malus to Attack
    character.current_defense += age_malus                                              # -- Apply Age Malus to Defense

    # Apply Perk Modifiers
    if character.perks:                                                                 # - If Character Has Perks
        for perk in character.perks:                                                    # -- For Each Perk
            if perk in PERK_STAT_MODIFIERS:                                             # --- If Perk Has Stat Modifiers
                modifiers = PERK_STAT_MODIFIERS[perk]                                   # ---- Get Modifiers
                for stat, values in modifiers.items():                                  # ---- For Each Stat Modifier
                    if stat == "melee":                                                 # ----- If Melee Modifier
                        character.current_speed += values.get("speed", 0)               # ------ Add Speed Modifier
                        character.current_attack += values.get("attack", 0)             # ------ Add Attack Modifier
                        character.current_defense += values.get("defense", 0)           # ------ Add Defense Modifier
                    elif stat == "all":                                                 # ----- If All Modifier
                        character.current_speed += values.get("speed", 0)               # ------ Add Speed Modifier
                        character.current_attack += values.get("attack", 0)             # ------ Add Attack Modifier
                        character.current_defense += values.get("defense", 0)           # ------ Add Defense Modifier

            if perk == "Indomitable T1":                                                # --- If Perk - Indomitable T1
                character.current_morale += 15                                          # ---- +15 Morale
                character.max_combatants = 4                                            # ---- Max Combatants +1
                character.major_injury_buff += 1                                        # ---- Ignore 1 Major Injury
            
            if perk == "Indomitable T2":                                                # --- If Perk - Indomitable T1
                character.current_morale += 30                                          # ---- +30 Morale
                character.max_combatants = 5                                            # ---- Max Combatants +2
                character.major_injury_buff += 2                                        # ---- Ignore 2 Major Injuries

            if perk == "Indomitable T3":                                                # --- If Perk - Indomitable T1
                character.current_morale += 45                                          # ---- +45 Morale
                character.max_combatants = 6                                            # ---- Max Combatants +3
                character.major_injury_buff += 3                                        # ---- Ignore 3 Major Injuries

# Stat Initialization Functions - Ranged
def ranged_initialization(character):
    """Initialize Ranged Stats for Character"""
    # Initialize Ranged Stats
    character.current_speed = 0                                                         # - Current Speed
    character.current_attack = 0                                                        # - Current Attack
    character.current_defense = 0                                                       # - Current Defense

    # Apply Age Malus
    age_malus = get_age_malus(character.age)                                            # - Get Age Malus
    character.current_speed += age_malus                                                # -- Apply Age Malus to Speed
    character.current_attack += age_malus                                               # -- Apply Age Malus to Attack
    character.current_defense += age_malus                                              # -- Apply Age Malus to Defense

    # Apply Perk Modifiers
    if character.perks:                                                                 # - If Character Has Perks
        for perk in character.perks:                                                    # -- For Each Perk
            if perk in PERK_STAT_MODIFIERS:                                             # --- If Perk Has Stat Modifiers
                modifiers = PERK_STAT_MODIFIERS[perk]                                   # ---- Get Modifiers
                for stat, values in modifiers.items():                                  # ---- For Each Stat Modifier
                    if stat == "ranged":                                                # ----- If Ranged Modifier
                        character.current_speed += values.get("speed", 0)               # ------ Add Speed Modifier
                        character.current_attack += values.get("attack", 0)             # ------ Add Attack Modifier
                        character.current_defense += values.get("defense", 0)           # ------ Add Defense Modifier
                    elif stat == "all":                                                 # ----- If All Modifier
                        character.current_speed += values.get("speed", 0)               # ------ Add Speed Modifier
                        character.current_attack += values.get("attack", 0)             # ------ Add Attack Modifier
                        character.current_defense += values.get("defense", 0)           # ------ Add Defense Modifier

            if perk == "Indomitable T1":                                                # --- If Perk - Indomitable T1
                character.current_morale += 15                                          # ---- Morale: 65
                character.max_combatants = 4                                            # ---- Max Combatants +1
            
            if perk == "Indomitable T2":                                                # --- If Perk - Indomitable T1
                character.current_morale += 30                                          # ---- Morale: 80
                character.max_combatants = 5                                            # ---- Max Combatants +2

            if perk == "Indomitable T3":                                                # --- If Perk - Indomitable T1
                character.current_morale += 45                                          # ---- Morale: 95
                character.max_combatants = 6                                            # ---- Max Combatants +3

# Stat Initialization Functions - Mixed
def mixed_initialization(character):
    """Remove Ranged Perks for Character"""
    # Remove Ranged Perk Modifiers
    if character.perks:                                                                 # - If Character Has Perks
        for perk in character.perks:                                                    # -- For Each Perk
            if perk in PERK_STAT_MODIFIERS:                                             # --- If Perk Has Stat Modifiers
                modifiers = PERK_STAT_MODIFIERS[perk]                                   # ---- Get Modifiers
                for stat, values in modifiers.items():                                  # ---- For Each Stat Modifier
                    if stat == "ranged":                                                # ----- If Mixed Modifier
                        character.current_speed -= values.get("speed", 0)               # ------ Add Speed Modifier
                        character.current_attack -= values.get("attack", 0)             # ------ Add Attack Modifier
                        character.current_defense -= values.get("defense", 0)           # ------ Add Defense Modifier

    # Apply Melee Perk Modifiers
    if character.perks:                                                                 # - If Character Has Perks
        for perk in character.perks:                                                    # -- For Each Perk
            if perk in PERK_STAT_MODIFIERS:                                             # --- If Perk Has Stat Modifiers
                modifiers = PERK_STAT_MODIFIERS[perk]                                   # ---- Get Modifiers
                for stat, values in modifiers.items():                                  # ---- For Each Stat Modifier
                    if stat == "melee":                                                 # ----- If Melee Modifier
                        character.current_speed += values.get("speed", 0)               # ------ Add Speed Modifier
                        character.current_attack += values.get("attack", 0)             # ------ Add Attack Modifier
                        character.current_defense += values.get("defense", 0)           # ------ Add Defense Modifier

            

######################################################################################################
# Dice
######################################################################################################

def roll_1d100():                                           # Roll 1d100   
    """Roll 1d100"""                                        
    return random.randint(1, 100)                           # Return number between 1 & 100

def roll_1d20():                                            # Roll 1d20
    """Roll 1d20"""
    return random.randint(1, 20)                            # Return number between 1 & 20

def roll_2d20():                                            # Roll 2d20
    """Roll 2d20"""
    d1 = random.randint(1, 20)                              # Roll 1d20
    d2 = random.randint(1, 20)                              # Roll 1d20
    return d1 + d2, (d1, d2)                                # Return sum of 2d20 and the rolls

def roll_3d5():                                             # Roll 3d5
    """Roll 3d5"""
    d1 = random.randint(1, 5)                               # Roll 1d5
    d2 = random.randint(1, 5)                               # Roll 1d5
    d3 = random.randint(1, 5)                               # Roll 1d5
    return d1 + d2 + d3, (d1, d2, d3)                       # Return sum of 3d5 and the rolls

######################################################################################################
# Injury Rolls
######################################################################################################

def primary_injury_roll(weapons):                           
    """Roll for Primary Injury - 1d100"""                    
    roll = roll_1d100()                                      # - Roll 1d100     

    if weapons.lower() == "steel":                          # -- Live Steel
        if 1 <= roll <= 25:                                 # --- 1-25    
            return "Death"                                  # ---- Death
        elif 26 <= roll <= 40:                              # --- 26-40
            crit = critical_injury()                        # ---- Roll Critical Injury
            return f"Critical Injury - {crit}"              # ---- Critical Injury
        elif 41 <= roll <= 70:                              # --- 41-70
            return "Major Injury"                           # ---- Major Injury
        elif 71 <= roll <= 100:                             # --- 71-100
            return "Minor Injury"
        
    elif weapons.lower() == "blunted":                      # -- Blunted Steel
        if 1 <= roll <= 20:                                 # --- 1-20
            return "Major Injury"                           # ---- Major Injury
        elif 21 <= roll <= 100:                             # --- 21-100
            return "Minor Injury"                           # ---- Minor Injury
        
    else:                                                   # -- Else
        return "Invalid steel type"                         # -- Invalid Weapon Type
    
def secondary_injury_roll(weapons):                          
    """Roll for Secondary Injury - 1d100"""                  
    roll = roll_1d100()                                      # - Roll 1d100   

    if weapons.lower() == "steel":                          # -- Live Steel
        if 1 <= roll <= 2:                                  # --- 1-2
            crit = critical_injury()                        # ---- Roll Critical Injury
            return f"Critical Injury - {crit}"              # ---- Critical Injury
        elif 3 <= roll <= 40:                               # --- 3-40
            return "Major Injury"                           # ---- Major Injury
        elif 41 <= roll <= 100:                             # --- 41-100
            return "Minor Injury"                           # ---- Minor Injury
        
    elif weapons.lower() == "blunted":                      # -- Blunted Steel
        if 1 <= roll <= 20:                                 # --- 1-20
            return "Major Injury"                           # ---- Major Injury
        elif 21 <= roll <= 100:                             # --- 21-100
            return "Minor Injury"                           # ---- Minor Injury
        
    else:                                                   # -- Else
        return "Invalid steel type"                         # -- Invalid Weapon Type

def critical_injury():                                      
    """Roll for Critical Injury - 1d20"""                    
    roll = roll_1d20()                                       # - Roll 1d20

    critical = {                                            # -- Critical Injury Effects
        1:  "Death",                                        # --- Death
        2:  "Brain Damage",                                 # --- Brain Damage
        3:  "Spine Damage / Paralysis",                     # --- Spine Damage / Paralysis
        4:  "Internal Organ Damage",                        # --- Internal Organ Damage
        5:  "Groin / Abdominal Damage",                     # --- Groin / Abdominal Damage
        6:  "Loss of Leg",                                  # --- Loss of Leg
        7:  "Loss of Arm",                                  # --- Loss of Arm
        8:  "Loss of Foot",                                 # --- Loss of Foot
        9:  "Loss of Hand",                                 # --- Loss of Hand               
        10: "Loss of Eye",                                  # --- Loss of Eye
        11: "Loss of Hearing",                              # --- Loss of Hearing
        12: "Mutilation / Severe Scarring",                 # --- Mutilation / Severe Scarring  
        13: "Pneumothorax",                                 # --- Pneumothorax
        14: "Severe Hemorrhage",                            # --- Severe Hemorrhage
        15: "Broken Leg",                                   # --- Broken Leg
        16: "Broken Arm",                                   # --- Broken Arm
        17: "Broken Foot",                                  # --- Broken Foot
        18: "Broken Hand",                                  # --- Broken Hand
        19: "Concussion",                                   # --- Concussion
        20: "Knocked Unconscious"                           # --- Knocked Unconscious
    }

    return critical[roll]                                   # -- Critical Injury

######################################################################################################
# Combat Functions
######################################################################################################

# Battlefield Duel Seeking
def combat_seeking(character):
    result = roll_1d100()                                           # - Roll D100
    if character.perks:                                             # - Character Perk Bonuses
        for perk in character.perks:                                # -- Iterate Through Perks
            if perk == "Battlefield Champion T1":                   # --- Battlefield Champion T1
                result += 5                                         # ---- Add 5
            elif perk == "Battlefield Champion T2":                 # --- Battlefield Champion T2
                result += 10                                        # ---- Add 10
            elif perk == "Indomitable T1":                          # --- Indomitable T1
                result += 5                                         # ---- Add 5
            elif perk == "Indomitable T2":                          # --- Indomitable T2
                result += 10                                        # ---- Add 10
            elif perk == "Indomitable T3":                          # --- Indomitable T3
                result += 15                                        # ---- Add 15
            elif perk == "Duelist T1":                              # --- Duelist T1
                result += 5                                         # ---- Add 5
            elif perk == "Duelist T2":                              # --- Duelist T2
                result += 10                                        # ---- Add 10
            elif perk == "Command & Presence":                      # --- Command & Presence
                result += 10                                        # ---- Add 10
    if result > 50:                                                 # - Success Threshold
        return "Character Finds Opponent!"                          # -- Found Opponent
    else:                                                           # - Failure Threshold
        return "Character Fails To Find Opponent!"                  # -- Did Not Find Opponent

# Side Initialization
def side_initialization(side_data):                                 
    side = []                                                       # - Initialize Side Array
    for spec in side_data:                                          # -- Iterate Through Side Data
        char = Character(                                           # --- Create Character
            spec["name"],                                           # ---- Name
            age=spec["age"],                                        # ---- Age
            perks=spec.get("perks", []),                            # ---- Perks
            injuries=spec.get("injuries", []),                      # ---- Injuries
            injury_threshold=spec.get("injury_threshold", 4),       # ---- Injury Threshold
            morale_threshold=spec.get("morale_threshold", 15)       # ---- Morale Threshold
        )
        side.append(char)                                           # --- Add Character To Side
    return side                                                     # - Return Side Array

# Melee vs Melee
def melee_melee(side1, side2, ct):
    # Side Initialization
    combat_side_one = side_initialization(side1)
    combat_side_two = side_initialization(side2)
    # Stat Initialization
    for c in combat_side_one + combat_side_two:
        melee_initialization(c)

    print("Combatants and their stats:")
    print("Side 1:")
    for c in combat_side_one:
        print(f"  {c.name} | Age: {c.age} | Perks: {c.perks} | Injuries: {c.injuries} | Injury Threshold: {c.injury_threshold} | Morale Threshold: {c.morale_threshold} | Speed: {c.current_speed} | Attack: {c.current_attack} | Defense: {c.current_defense} | Morale: {c.current_morale}")
    print("Side 2:")
    for c in combat_side_two:
        print(f"  {c.name} | Age: {c.age} | Perks: {c.perks} | Injuries: {c.injuries} | Injury Threshold: {c.injury_threshold} | Morale Threshold: {c.morale_threshold} | Speed: {c.current_speed} | Attack: {c.current_attack} | Defense: {c.current_defense} | Morale: {c.current_morale}")

    while len(combat_side_one) > 0 and len(combat_side_two) > 0:

        # Roll Initiative
        # Side One
        combat_side_one_initiative = []
        for c in combat_side_one:
            initiative_sum, _ = roll_2d20()
            combat_side_one_initiative.append(initiative_sum + c.current_speed)
            if 0 in _:
                c.crit_fail = 1
            if 20 in _:
                c.crit_success = 1
            if 19 in _ and "Duelist T3" in c.perks:
                c.crit_success = 1
            if 0 in _ and 20 in _:
                c.crit_fail = 0
                c.crit_success = 0
        # Side Two
        combat_side_two_initiative = []
        for c in combat_side_two:
            initiative_sum, _ = roll_2d20()
            combat_side_two_initiative.append(initiative_sum + c.current_speed)
            if 0 in _:
                c.crit_fail = 1
            if 20 in _:
                c.crit_success = 1
            if 19 in _ and "Duelist T3" in c.perks:
                c.crit_success = 1
            if 0 in _ and 20 in _:
                c.crit_fail = 0
                c.crit_success = 0

        # Sort combat_side_one and combat_side_one_initiative by initiative (ascending)
        side_one_pairs = list(zip(combat_side_one_initiative, combat_side_one))
        side_one_pairs.sort(key=lambda x: x[0])
        combat_side_one_initiative, combat_side_one = zip(*side_one_pairs)
        combat_side_one_initiative = list(combat_side_one_initiative)
        combat_side_one = list(combat_side_one)

        # Sort combat_side_two and combat_side_two_initiative by initiative (ascending)
        side_two_pairs = list(zip(combat_side_two_initiative, combat_side_two))
        side_two_pairs.sort(key=lambda x: x[0])
        combat_side_two_initiative, combat_side_two = zip(*side_two_pairs)
        combat_side_two_initiative = list(combat_side_two_initiative)
        combat_side_two = list(combat_side_two)

        # Print initiative rolls for each character
        # print("Initiative Rolls:")
        # for idx, c in enumerate(combat_side_one):
            # print(f"  Side 1 - {c.name}: {combat_side_one_initiative[idx]}")
        # for idx, c in enumerate(combat_side_two):
            # print(f"  Side 2 - {c.name}: {combat_side_two_initiative[idx]}")

        # Check Initiative
        # Iterate Through Combat Side One
        i = 0
        while i < len(combat_side_one):
            c1 = combat_side_one[i]
            j = 0
            while j < len(combat_side_two):
                c2 = combat_side_two[j]
                # If Combatant Has Rolled Higher
                if ((combat_side_one_initiative[i] > combat_side_two_initiative[j]) and c1.currently_engaging == 0) or (combat_side_two[j].combatants_faced >= combat_side_two[j].max_combatants):
                    # Critical Strike
                    if (combat_side_one[i].crit_strike == 1):
                        if((combat_side_two_initiative[j].current_speed > combat_side_two_initiative[j].current_attack) and (combat_side_two_initiative[j].current_speed > combat_side_two_initiative[j].current_defense)):
                            combat_side_two[j].current_speed -= 2
                        elif((combat_side_two_initiative[j].current_attack > combat_side_two_initiative[j].current_speed) and (combat_side_two_initiative[j].current_attack > combat_side_two_initiative[j].current_defense)):
                            combat_side_two[j].current_attack -= 2
                        elif((combat_side_two_initiative[j].current_defense > combat_side_two_initiative[j].current_speed) and (combat_side_two_initiative[j].current_defense > combat_side_two_initiative[j].current_attack)):
                            combat_side_two[j].current_defense -= 2
                        critical_strike_injury = secondary_injury_roll(ct)
                        if isinstance(critical_strike_injury, str) and "Critical Injury" in critical_strike_injury:
                            combat_side_two.pop(i)
                            combat_side_two_initiative.pop(i)
                        if critical_strike_injury == "Major Injury":
                            combat_side_two[j].major_injuries += 1
                        if critical_strike_injury == "Major Injury" and combat_side_two[j].major_injuries > combat_side_two[j].major_injury_buff:
                            combat_side_two[i].current_speed -= 2
                            combat_side_two[i].current_attack -= 2
                            combat_side_two[i].current_defense -= 2
                        if critical_strike_injury == "Minor Injury":
                            combat_side_two[i].current_speed -= 1
                            combat_side_two[i].current_attack -= 1
                            combat_side_two[i].current_defense -= 1
                        print(critical_strike_injury)
                    c1.currently_engaging = 1
                    c2.combatants_faced += 1
                    attack_sum, _ = roll_3d5()
                    attack_roll = ((attack_sum + c1.current_attack) - c2.current_defense)
                    c2.current_morale -= attack_roll
                    # print(f"{c2.name}'s Current Morale: {c2.current_morale}")
                    if (c2.current_morale <= 0) or (c2.current_morale <= c2.morale_threshold) or (len(c2.injuries) >= c2.injury_threshold):
                        # print(f"{combat_side_two[j].name} Defeated")
                        if(c2.current_morale <= 0):
                            morale_injury_roll = primary_injury_roll(ct)
                            print(morale_injury_roll)
                        combat_side_two.pop(j)
                        combat_side_two_initiative.pop(j)
                        continue  # Don't increment j, as list has shifted
                j += 1
            i += 1
            if (c1.currently_engaging == 0) and c1.crit_fail == 1:
                if((combat_side_one[i].current_speed > combat_side_one[i].current_attack) and (combat_side_one[i].current_speed > combat_side_one[i].current_defense)):
                    combat_side_one[i].current_speed -= 2
                elif((combat_side_one[i].current_attack > combat_side_one[i].current_speed) and (combat_side_one[i].current_attack > combat_side_one[i].current_defense)):
                    combat_side_one[i].current_attack -= 2
                elif((combat_side_one[i].current_defense > combat_side_one[i].current_speed) and (combat_side_one[i].current_defense > combat_side_one[i].current_attack)):
                    combat_side_one[i].current_defense -= 2
                critical_fail_injury = secondary_injury_roll(ct)
                if isinstance(critical_fail_injury, str) and "Critical Injury" in critical_fail_injury:
                    combat_side_one.pop(i)
                    combat_side_one_initiative.pop(i)
                if critical_fail_injury == "Major Injury":
                    combat_side_one[i].major_injuries += 1
                if critical_fail_injury == "Major Injury" and combat_side_one[i].major_injuries > combat_side_one[i].major_injury_buff:
                    combat_side_one[i].current_speed -= 2
                    combat_side_one[i].current_attack -= 2
                    combat_side_one[i].current_defense -= 2
                if critical_fail_injury == "Minor Injury":
                    combat_side_one[i].current_speed -= 1
                    combat_side_one[i].current_attack -= 1
                    combat_side_one[i].current_defense -= 1
                print(critical_fail_injury)

        # Iterate Through Combat Side Two
        i = 0
        while i < len(combat_side_two):
            c2 = combat_side_two[i]
            j = 0
            while j < len(combat_side_one):
                c1 = combat_side_one[j]
                # If Combatant Has Rolled Higher
                if ((combat_side_two_initiative[i] > combat_side_one_initiative[j]) and c2.currently_engaging == 0) or (combat_side_one[j].combatants_faced >= combat_side_one[j].max_combatants):
                    # Critical Strike
                    if (combat_side_two[i].crit_strike == 1):
                        if((combat_side_one_initiative[j].current_speed > combat_side_one_initiative[j].current_attack) and (combat_side_one_initiative[j].current_speed > combat_side_one_initiative[j].current_defense)):
                            combat_side_one[j].current_speed -= 2
                        elif((combat_side_one_initiative[j].current_attack > combat_side_one_initiative[j].current_speed) and (combat_side_one_initiative[j].current_attack > combat_side_one_initiative[j].current_defense)):
                            combat_side_one[j].current_attack -= 2
                        elif((combat_side_one_initiative[j].current_defense > combat_side_one_initiative[j].current_speed) and (combat_side_one_initiative[j].current_defense > combat_side_one_initiative[j].current_attack)):
                            combat_side_one[j].current_defense -= 2
                        critical_strike_injury = secondary_injury_roll(ct)
                        if isinstance(critical_strike_injury, str) and "Critical Injury" in critical_strike_injury:
                            combat_side_one.pop(i)
                            combat_side_one_initiative.pop(i)
                        if critical_strike_injury == "Major Injury":
                            combat_side_one[j].major_injuries += 1
                        if critical_strike_injury == "Major Injury" and combat_side_one[j].major_injuries > combat_side_one[j].major_injury_buff:
                            combat_side_one[i].current_speed -= 2
                            combat_side_one[i].current_attack -= 2
                            combat_side_one[i].current_defense -= 2
                        if critical_strike_injury == "Minor Injury":
                            combat_side_one[i].current_speed -= 1
                            combat_side_one[i].current_attack -= 1
                            combat_side_one[i].current_defense -= 1
                        print(critical_strike_injury)
                    # One Combatant Only
                    c2.currently_engaging = 1
                    c1.combatants_faced += 1
                    # Roll Attack
                    attack_sum, _ = roll_3d5()
                    attack_roll = ((attack_sum + c2.current_attack) - c1.current_defense)
                    c1.current_morale -= attack_roll
                    # print(f"{c1.name}'s Current Morale: {c1.current_morale}")
                    if (c1.current_morale <= 0) or (c1.current_morale <= c1.morale_threshold) or (len(c1.injuries) >= c1.injury_threshold):
                        # print(f"{combat_side_one[j].name} Defeated")
                        if(c1.current_morale <= 0):
                            morale_injury_roll = primary_injury_roll(ct)
                            print(morale_injury_roll)
                        combat_side_one.pop(j)
                        combat_side_one_initiative.pop(j)
                        continue  # Don't increment j, as list has shifted
                j += 1
            
            if (c2.currently_engaging == 0) and c2.crit_fail == 1:
                if((combat_side_two[i].current_speed > combat_side_two[i].current_attack) and (combat_side_two[i].current_speed > combat_side_two[i].current_defense)):
                    combat_side_two[i].current_speed -= 2
                elif((combat_side_two[i].current_attack > combat_side_two[i].current_speed) and (combat_side_two[i].current_attack > combat_side_two[i].current_defense)):
                    combat_side_two[i].current_attack -= 2
                elif((combat_side_two[i].current_defense > combat_side_two[i].current_speed) and (combat_side_two[i].current_defense > combat_side_two[i].current_attack)):
                    combat_side_two[i].current_defense -= 2
                critical_fail_injury = secondary_injury_roll(ct)
                if isinstance(critical_fail_injury, str) and "Critical Injury" in critical_fail_injury:
                    combat_side_two.pop(i)
                    combat_side_two_initiative.pop(i)
                if critical_fail_injury == "Major Injury":
                    combat_side_two[i].current_speed -= 2
                    combat_side_two[i].current_attack -= 2
                    combat_side_two[i].current_defense -= 2
                if critical_fail_injury == "Minor Injury":
                    combat_side_two[i].current_speed -= 1
                    combat_side_two[i].current_attack -= 1
                    combat_side_two[i].current_defense -= 1
                print(critical_fail_injury)
            i += 1
        
        # End Of Round
        # Stalemate
        stalemate = 1
        for c in combat_side_one:
            if c.currently_engaging == 1:
                stalemate = 0
        for c in combat_side_two:
            if c.currently_engaging == 1:
                stalemate = 0
        if stalemate == 1:
            print("This round has ended in a stalemate, neither side have made progress.")

        # End Of Round
        combat_side_one_initiative = []
        combat_side_two_initiative = []
        # Prepare For Next Round
        for c in combat_side_one:
            c.currently_engaging = 0
            c.crit_success = 0
            c.crit_fail = 0
            c.combatants_faced = 0
        # Prepare For Next Round
        for c in combat_side_two:
            c.currently_engaging = 0
            c.crit_success = 0
            c.crit_fail = 0
            c.combatants_faced = 0

    if len(combat_side_one) == 0:
        print("Side two wins the duel!")

    if len(combat_side_two) == 0:
        print("Side one wins the duel!")

# Ranged vs Melee
def ranged_melee(side1, side2, ct):
    # Side Initialization
    combat_side_one = side_initialization(side1)
    combat_side_two = side_initialization(side2)
    # Stat Initialization
    for i in range(len(combat_side_one)):
        ranged_initialization(combat_side_one[i])
    for j in range(len(combat_side_two)):
        melee_initialization(combat_side_two[j])


    print("Combatants and their stats:")
    print("Side 1:")
    for c in combat_side_one:
        print(f"  {c.name} | Age: {c.age} | Perks: {c.perks} | Injuries: {c.injuries} | Injury Threshold: {c.injury_threshold} | Morale Threshold: {c.morale_threshold} | Speed: {c.current_speed} | Attack: {c.current_attack} | Defense: {c.current_defense} | Morale: {c.current_morale}")
    print("Side 2:")
    for c in combat_side_two:
        print(f"  {c.name} | Age: {c.age} | Perks: {c.perks} | Injuries: {c.injuries} | Injury Threshold: {c.injury_threshold} | Morale Threshold: {c.morale_threshold} | Speed: {c.current_speed} | Attack: {c.current_attack} | Defense: {c.current_defense} | Morale: {c.current_morale}") 
    
    # Stage One - Ranged Attacks
    # Keep Track
    ranged_rounds = 0
    while len(combat_side_one) > 0 and len(combat_side_two) > 0:

        combat_side_one_initiative = []
        for c in combat_side_one:
            initiative_sum, _ = roll_2d20()
            combat_side_one_initiative.append(initiative_sum + c.current_speed)
            if 0 in _:
                c.crit_fail = 1
            if 20 in _:
                c.crit_success = 1
            if 0 in _ and 20 in _:
                c.crit_fail = 0
                c.crit_success = 0
        
        # Sort combat_side_one and combat_side_one_initiative by initiative (ascending)
        side_one_pairs = list(zip(combat_side_one_initiative, combat_side_one))
        side_one_pairs.sort(key=lambda x: x[0])
        combat_side_one_initiative, combat_side_one = zip(*side_one_pairs)
        combat_side_one_initiative = list(combat_side_one_initiative)
        combat_side_one = list(combat_side_one)

        # Check Initiative
        # Iterate Through Combat Side One
        i = 0
        while i < len(combat_side_one):
            c1 = combat_side_one[i]
            j = 0
            while j < len(combat_side_two):
                c2 = combat_side_two[j]
                # If Combatant Has Rolled Higher
                if (((combat_side_one_initiative[i] >= 30) and c1.currently_engaging == 0) or (combat_side_two[j].combatants_faced >= combat_side_two[j].max_combatants)) and (c1.max_mixed_rounds >= ranged_rounds):
                    # Critical Strike
                    if (combat_side_one[i].crit_strike == 1):
                        if((combat_side_two[j].current_speed > combat_side_two[j].current_attack) and (combat_side_two[j].current_speed > combat_side_two[j].current_defense)):
                            combat_side_two[j].current_speed -= 2
                        elif((combat_side_two[j].current_attack > combat_side_two[j].current_speed) and (combat_side_two[j].current_attack > combat_side_two[j].current_defense)):
                            combat_side_two[j].current_attack -= 2
                        elif((combat_side_two[j].current_defense > combat_side_two[j].current_speed) and (combat_side_two[j].current_defense > combat_side_two[j].current_attack)):
                            combat_side_two[j].current_defense -= 2
                        critical_strike_injury = secondary_injury_roll(ct)
                        if isinstance(critical_strike_injury, str) and "Critical Injury" in critical_strike_injury:
                            combat_side_two.pop(i)
                            combat_side_two.pop(i)
                        if critical_strike_injury == "Major Injury":
                            combat_side_two[i].current_speed -= 2
                            combat_side_two[i].current_attack -= 2
                            combat_side_two[i].current_defense -= 2
                        if critical_strike_injury == "Minor Injury":
                            combat_side_two[i].current_speed -= 1
                            combat_side_two[i].current_attack -= 1
                            combat_side_two[i].current_defense -= 1
                        print(critical_strike_injury)
                    c1.currently_engaging = 1
                    c2.combatants_faced += 1
                    attack_sum, _ = roll_3d5()
                    attack_roll = ((attack_sum + c1.current_attack) - c2.current_defense)
                    c2.current_morale -= attack_roll
                    # print(f"{c2.name}'s Current Morale: {c2.current_morale}")
                    if (c2.current_morale <= 0) or (c2.current_morale <= c2.morale_threshold) or (len(c2.injuries) >= c2.injury_threshold):
                        # print(f"{combat_side_two[j].name} Defeated")
                        if(c2.current_morale <= 0):
                            morale_injury_roll = primary_injury_roll(ct)
                            print(morale_injury_roll)
                        combat_side_two.pop(j)
                        combat_side_two.pop(j)
                        continue  # Don't increment j, as list has shifted
                j += 1
            i += 1
            if ((c1.currently_engaging == 0) and c1.crit_fail == 1) and (c1.max_mixed_rounds >= ranged_rounds):
                if((combat_side_two[i].current_speed > combat_side_two[i].current_attack) and (combat_side_two[i].current_speed > combat_side_two[i].current_defense)):
                    combat_side_two[i].current_speed -= 2
                elif((combat_side_two[i].current_attack > combat_side_two[i].current_speed) and (combat_side_two[i].current_attack > combat_side_two[i].current_defense)):
                    combat_side_two[i].current_attack -= 2
                elif((combat_side_two[i].current_defense > combat_side_two[i].current_speed) and (combat_side_two[i].current_defense > combat_side_two[i].current_attack)):
                    combat_side_two[i].current_defense -= 2
                critical_fail_injury = secondary_injury_roll(ct)
                if isinstance(critical_fail_injury, str) and "Critical Injury" in critical_fail_injury:
                    combat_side_one.pop(i)
                    combat_side_one_initiative.pop(i)
                if critical_fail_injury == "Major Injury":
                    combat_side_one[i].current_speed -= 2
                    combat_side_one[i].current_attack -= 2
                    combat_side_one[i].current_defense -= 2
                if critical_fail_injury == "Minor Injury":
                    combat_side_one[i].current_speed -= 1
                    combat_side_one[i].current_attack -= 1
                    combat_side_one[i].current_defense -= 1
                print(critical_fail_injury)

        ranged_rounds += 1

        # End Of Round
        # Stalemate
        stalemate = 1
        for c in combat_side_one:
            if c.currently_engaging == 1:
                stalemate = 0
        for c in combat_side_two:
            if c.currently_engaging == 1:
                stalemate = 0
        if stalemate == 1:
            print("This round has ended in a stalemate, neither side have made progress.")

        # End Of Round
        combat_side_one_initiative = []
        # Prepare For Next Round
        for c in combat_side_one:
            c.currently_engaging = 0
            c.crit_success = 0
            c.crit_fail = 0
            c.combatants_faced = 0
        # Prepare For Next Round
        for c in combat_side_two:
            c.currently_engaging = 0
            c.crit_success = 0
            c.crit_fail = 0
            c.combatants_faced = 0
        # Are We Done?
        continue_duel = 0
        for c in combat_side_one:
            if c.max_mixed_rounds >= ranged_rounds:
                continue_duel += 1
        
        if continue_duel == 0:
            break
    
    # Stage 2
    while len(combat_side_one) > 0 and len(combat_side_two) > 0:

        # Iterate Through Combat Side Two
        i = 0
        while i < len(combat_side_two):
            c2 = combat_side_two[i]
            j = 0
            while j < len(combat_side_one):
                c1 = combat_side_one[j]
                # Critical Strike
                if (combat_side_two[i].crit_strike == 1):
                    if((combat_side_one[j].current_speed > combat_side_one[j].current_attack) and (combat_side_one[j].current_speed > combat_side_one[j].current_defense)):
                        combat_side_one[j].current_speed -= 2
                    elif((combat_side_one[j].current_attack > combat_side_one[j].current_speed) and (combat_side_one[j].current_attack > combat_side_one[j].current_defense)):
                        combat_side_one[j].current_attack -= 2
                    elif((combat_side_one[j].current_defense > combat_side_one[j].current_speed) and (combat_side_one[j].current_defense > combat_side_one[j].current_attack)):
                        combat_side_one[j].current_defense -= 2
                    critical_strike_injury = secondary_injury_roll(ct)
                    if isinstance(critical_strike_injury, str) and "Critical Injury" in critical_strike_injury:
                        combat_side_one.pop(i)
                    if critical_strike_injury == "Major Injury":
                        combat_side_one[i].current_speed -= 2
                        combat_side_one[i].current_attack -= 2
                        combat_side_one[i].current_defense -= 2
                    if critical_strike_injury == "Minor Injury":
                        combat_side_one[i].current_speed -= 1
                        combat_side_one[i].current_attack -= 1
                        combat_side_one[i].current_defense -= 1
                    print(critical_strike_injury)
                # One Combatant Only
                c2.currently_engaging = 1
                c1.combatants_faced += 1
                # Roll Attack
                attack_sum, _ = roll_3d5()
                attack_roll = ((attack_sum + c2.current_attack) - c1.current_defense)
                c1.current_morale -= attack_roll
                # print(f"{c1.name}'s Current Morale: {c1.current_morale}")
                if (c1.current_morale <= 0) or (c1.current_morale <= c1.morale_threshold) or (len(c1.injuries) >= c1.injury_threshold):
                    # print(f"{combat_side_one[j].name} Defeated")
                    if(c1.current_morale <= 0):
                        morale_injury_roll = primary_injury_roll(ct)
                        print(morale_injury_roll)
                    combat_side_one.pop(j)
                    continue  # Don't increment j, as list has shifted
                j += 1
            
            if (c2.currently_engaging == 0) and c2.crit_fail == 1:
                if((combat_side_two[i].current_speed > combat_side_two[i].current_attack) and (combat_side_two[i].current_speed > combat_side_two[i].current_defense)):
                    combat_side_two[i].current_speed -= 2
                elif((combat_side_two[i].current_attack > combat_side_two[i].current_speed) and (combat_side_two[i].current_attack > combat_side_two[i].current_defense)):
                    combat_side_two[i].current_attack -= 2
                elif((combat_side_two[i].current_defense > combat_side_two[i].current_speed) and (combat_side_two[i].current_defense > combat_side_two[i].current_attack)):
                    combat_side_two[i].current_defense -= 2
                critical_fail_injury = secondary_injury_roll(ct)
                if isinstance(critical_fail_injury, str) and "Critical Injury" in critical_fail_injury:
                    combat_side_two.pop(i)
                if critical_fail_injury == "Major Injury":
                    combat_side_two[i].current_speed -= 2
                    combat_side_two[i].current_attack -= 2
                    combat_side_two[i].current_defense -= 2
                if critical_fail_injury == "Minor Injury":
                    combat_side_two[i].current_speed -= 1
                    combat_side_two[i].current_attack -= 1
                    combat_side_two[i].current_defense -= 1
                print(critical_fail_injury)
            i += 1
        
        # End Of Round
        # Stalemate
        stalemate = 1
        for c in combat_side_one:
            if c.currently_engaging == 1:
                stalemate = 0
        for c in combat_side_two:
            if c.currently_engaging == 1:
                stalemate = 0
        if stalemate == 1:
            print("This round has ended in a stalemate, neither side have made progress.")

        # End Of Round
        # Prepare For Next Round
        for c in combat_side_one:
            c.currently_engaging = 0
            c.crit_success = 0
            c.crit_fail = 0
            c.combatants_faced = 0
        # Prepare For Next Round
        for c in combat_side_two:
            c.currently_engaging = 0
            c.crit_success = 0
            c.crit_fail = 0
            c.combatants_faced = 0

        break

    # Switch Context Initialization
    for i in range(len(combat_side_one)):
        mixed_initialization(combat_side_one[i])

    # Stage 3
    while len(combat_side_one) > 0 and len(combat_side_two) > 0:

        # Roll Initiative
        # Side One
        combat_side_one_initiative = []
        for c in combat_side_one:
            initiative_sum, _ = roll_2d20()
            combat_side_one_initiative.append(initiative_sum + c.current_speed)
            if 0 in _:
                c.crit_fail = 1
            if 20 in _:
                c.crit_success = 1
            if 0 in _ and 20 in _:
                c.crit_fail = 0
                c.crit_success = 0
        # Side Two
        combat_side_two_initiative = []
        for c in combat_side_two:
            initiative_sum, _ = roll_2d20()
            combat_side_two_initiative.append(initiative_sum + c.current_speed)
            if 0 in _:
                c.crit_fail = 1
            if 20 in _:
                c.crit_success = 1
            if 0 in _ and 20 in _:
                c.crit_fail = 0
                c.crit_success = 0

        # Sort combat_side_one and combat_side_one_initiative by initiative (ascending)
        side_one_pairs = list(zip(combat_side_one_initiative, combat_side_one))
        side_one_pairs.sort(key=lambda x: x[0])
        combat_side_one_initiative, combat_side_one = zip(*side_one_pairs)
        combat_side_one_initiative = list(combat_side_one_initiative)
        combat_side_one = list(combat_side_one)

        # Sort combat_side_two and combat_side_two_initiative by initiative (ascending)
        side_two_pairs = list(zip(combat_side_two_initiative, combat_side_two))
        side_two_pairs.sort(key=lambda x: x[0])
        combat_side_two_initiative, combat_side_two = zip(*side_two_pairs)
        combat_side_two_initiative = list(combat_side_two_initiative)
        combat_side_two = list(combat_side_two)

        # Print initiative rolls for each character
        # print("Initiative Rolls:")
        # for idx, c in enumerate(combat_side_one):
            # print(f"  Side 1 - {c.name}: {combat_side_one_initiative[idx]}")
        # for idx, c in enumerate(combat_side_two):
            # print(f"  Side 2 - {c.name}: {combat_side_two_initiative[idx]}")

        # Check Initiative
        # Iterate Through Combat Side One
        i = 0
        while i < len(combat_side_one):
            c1 = combat_side_one[i]
            j = 0
            while j < len(combat_side_two):
                c2 = combat_side_two[j]
                # If Combatant Has Rolled Higher
                if ((combat_side_one_initiative[i] > combat_side_two_initiative[j]) and c1.currently_engaging == 0) or (combat_side_two[j].combatants_faced >= combat_side_two[j].max_combatants):
                    # Critical Strike
                    if (combat_side_one[i].crit_strike == 1):
                        if((combat_side_two_initiative[j].current_speed > combat_side_two_initiative[j].current_attack) and (combat_side_two_initiative[j].current_speed > combat_side_two_initiative[j].current_defense)):
                            combat_side_two[j].current_speed -= 2
                        elif((combat_side_two_initiative[j].current_attack > combat_side_two_initiative[j].current_speed) and (combat_side_two_initiative[j].current_attack > combat_side_two_initiative[j].current_defense)):
                            combat_side_two[j].current_attack -= 2
                        elif((combat_side_two_initiative[j].current_defense > combat_side_two_initiative[j].current_speed) and (combat_side_two_initiative[j].current_defense > combat_side_two_initiative[j].current_attack)):
                            combat_side_two[j].current_defense -= 2
                        critical_strike_injury = secondary_injury_roll(ct)
                        if isinstance(critical_strike_injury, str) and "Critical Injury" in critical_strike_injury:
                            combat_side_two.pop(i)
                            combat_side_two_initiative.pop(i)
                        if critical_strike_injury == "Major Injury":
                            combat_side_two[i].current_speed -= 2
                            combat_side_two[i].current_attack -= 2
                            combat_side_two[i].current_defense -= 2
                        if critical_strike_injury == "Minor Injury":
                            combat_side_two[i].current_speed -= 1
                            combat_side_two[i].current_attack -= 1
                            combat_side_two[i].current_defense -= 1
                        print(critical_strike_injury)
                    c1.currently_engaging = 1
                    c2.combatants_faced += 1
                    attack_sum, _ = roll_3d5()
                    attack_roll = ((attack_sum + c1.current_attack) - c2.current_defense)
                    c2.current_morale -= attack_roll
                    # print(f"{c2.name}'s Current Morale: {c2.current_morale}")
                    if (c2.current_morale <= 0) or (c2.current_morale <= c2.morale_threshold) or (len(c2.injuries) >= c2.injury_threshold):
                        # print(f"{combat_side_two[j].name} Defeated")
                        if(c2.current_morale <= 0):
                            morale_injury_roll = primary_injury_roll(ct)
                            print(morale_injury_roll)
                        combat_side_two.pop(j)
                        combat_side_two_initiative.pop(j)
                        continue  # Don't increment j, as list has shifted
                j += 1
            i += 1
            if (c1.currently_engaging == 0) and c1.crit_fail == 1:
                if((combat_side_two[i].current_speed > combat_side_two[i].current_attack) and (combat_side_two[i].current_speed > combat_side_two[i].current_defense)):
                    combat_side_two[i].current_speed -= 2
                elif((combat_side_two[i].current_attack > combat_side_two[i].current_speed) and (combat_side_two[i].current_attack > combat_side_two[i].current_defense)):
                    combat_side_two[i].current_attack -= 2
                elif((combat_side_two[i].current_defense > combat_side_two[i].current_speed) and (combat_side_two[i].current_defense > combat_side_two[i].current_attack)):
                    combat_side_two[i].current_defense -= 2
                critical_fail_injury = secondary_injury_roll(ct)
                if isinstance(critical_fail_injury, str) and "Critical Injury" in critical_fail_injury:
                    combat_side_one.pop(i)
                    combat_side_one_initiative.pop(i)
                if critical_fail_injury == "Major Injury":
                    combat_side_one[i].current_speed -= 2
                    combat_side_one[i].current_attack -= 2
                    combat_side_one[i].current_defense -= 2
                if critical_fail_injury == "Minor Injury":
                    combat_side_one[i].current_speed -= 1
                    combat_side_one[i].current_attack -= 1
                    combat_side_one[i].current_defense -= 1
                print(critical_fail_injury)

        # Iterate Through Combat Side Two
        i = 0
        while i < len(combat_side_two):
            c2 = combat_side_two[i]
            j = 0
            while j < len(combat_side_one):
                c1 = combat_side_one[j]
                # If Combatant Has Rolled Higher
                if ((combat_side_two_initiative[i] > combat_side_one_initiative[j]) and c2.currently_engaging == 0) or (combat_side_one[j].combatants_faced >= combat_side_one[j].max_combatants):
                    # Critical Strike
                    if (combat_side_two[i].crit_strike == 1):
                        if((combat_side_one_initiative[j].current_speed > combat_side_one_initiative[j].current_attack) and (combat_side_one_initiative[j].current_speed > combat_side_one_initiative[j].current_defense)):
                            combat_side_one[j].current_speed -= 2
                        elif((combat_side_one_initiative[j].current_attack > combat_side_one_initiative[j].current_speed) and (combat_side_one_initiative[j].current_attack > combat_side_one_initiative[j].current_defense)):
                            combat_side_one[j].current_attack -= 2
                        elif((combat_side_one_initiative[j].current_defense > combat_side_one_initiative[j].current_speed) and (combat_side_one_initiative[j].current_defense > combat_side_one_initiative[j].current_attack)):
                            combat_side_one[j].current_defense -= 2
                        critical_strike_injury = secondary_injury_roll(ct)
                        if isinstance(critical_strike_injury, str) and "Critical Injury" in critical_strike_injury:
                            combat_side_one.pop(i)
                            combat_side_one_initiative.pop(i)
                        if critical_strike_injury == "Major Injury":
                            combat_side_one[i].current_speed -= 2
                            combat_side_one[i].current_attack -= 2
                            combat_side_one[i].current_defense -= 2
                        if critical_strike_injury == "Minor Injury":
                            combat_side_one[i].current_speed -= 1
                            combat_side_one[i].current_attack -= 1
                            combat_side_one[i].current_defense -= 1
                        print(critical_strike_injury)
                    # One Combatant Only
                    c2.currently_engaging = 1
                    c1.combatants_faced += 1
                    # Roll Attack
                    attack_sum, _ = roll_3d5()
                    attack_roll = ((attack_sum + c2.current_attack) - c1.current_defense)
                    c1.current_morale -= attack_roll
                    # print(f"{c1.name}'s Current Morale: {c1.current_morale}")
                    if (c1.current_morale <= 0) or (c1.current_morale <= c1.morale_threshold) or (len(c1.injuries) >= c1.injury_threshold):
                        # print(f"{combat_side_one[j].name} Defeated")
                        if(c1.current_morale <= 0):
                            morale_injury_roll = primary_injury_roll(ct)
                            print(morale_injury_roll)
                        combat_side_one.pop(j)
                        combat_side_one_initiative.pop(j)
                        continue  # Don't increment j, as list has shifted
                j += 1
            
            if (c2.currently_engaging == 0) and c2.crit_fail == 1:
                if((combat_side_two[i].current_speed > combat_side_two[i].current_attack) and (combat_side_two[i].current_speed > combat_side_two[i].current_defense)):
                    combat_side_two[i].current_speed -= 2
                elif((combat_side_two[i].current_attack > combat_side_two[i].current_speed) and (combat_side_two[i].current_attack > combat_side_two[i].current_defense)):
                    combat_side_two[i].current_attack -= 2
                elif((combat_side_two[i].current_defense > combat_side_two[i].current_speed) and (combat_side_two[i].current_defense > combat_side_two[i].current_attack)):
                    combat_side_two[i].current_defense -= 2
                critical_fail_injury = secondary_injury_roll(ct)
                if isinstance(critical_fail_injury, str) and "Critical Injury" in critical_fail_injury:
                    combat_side_two.pop(i)
                    combat_side_two_initiative.pop(i)
                if critical_fail_injury == "Major Injury":
                    combat_side_two[i].current_speed -= 2
                    combat_side_two[i].current_attack -= 2
                    combat_side_two[i].current_defense -= 2
                if critical_fail_injury == "Minor Injury":
                    combat_side_two[i].current_speed -= 1
                    combat_side_two[i].current_attack -= 1
                    combat_side_two[i].current_defense -= 1
                print(critical_fail_injury)
            i += 1
        
        # End Of Round
        # Stalemate
        stalemate = 1
        for c in combat_side_one:
            if c.currently_engaging == 1:
                stalemate = 0
        for c in combat_side_two:
            if c.currently_engaging == 1:
                stalemate = 0
        if stalemate == 1:
            print("This round has ended in a stalemate, neither side have made progress.")

        # End Of Round
        combat_side_one_initiative = []
        combat_side_two_initiative = []
        # Prepare For Next Round
        for c in combat_side_one:
            c.currently_engaging = 0
            c.crit_success = 0
            c.crit_fail = 0
            c.combatants_faced = 0
        # Prepare For Next Round
        for c in combat_side_two:
            c.currently_engaging = 0
            c.crit_success = 0
            c.crit_fail = 0
            c.combatants_faced = 0

    if len(combat_side_one) == 0:
        print("Side two wins the duel!")

    if len(combat_side_two) == 0:
        print("Side one wins the duel!")
    
# Ranged vs Ranged
def ranged_ranged(side1, side2, ct):
    # Side Initialization
    combat_side_one = side_initialization(side1)
    combat_side_two = side_initialization(side2)
    # Stat Initialization
    for c in combat_side_one + combat_side_two:
        ranged_initialization(c)
    
    print("Combatants and their stats:")
    print("Side 1:")
    for c in combat_side_one:
        print(f"  {c.name} | Age: {c.age} | Perks: {c.perks} | Injuries: {c.injuries} | Injury Threshold: {c.injury_threshold} | Morale Threshold: {c.morale_threshold} | Speed: {c.current_speed} | Attack: {c.current_attack} | Defense: {c.current_defense} | Morale: {c.current_morale}")
    print("Side 2:")
    for c in combat_side_two:
        print(f"  {c.name} | Age: {c.age} | Perks: {c.perks} | Injuries: {c.injuries} | Injury Threshold: {c.injury_threshold} | Morale Threshold: {c.morale_threshold} | Speed: {c.current_speed} | Attack: {c.current_attack} | Defense: {c.current_defense} | Morale: {c.current_morale}")

    while len(combat_side_one) > 0 and len(combat_side_two) > 0:

        # Roll Initiative
        # Side One
        combat_side_one_initiative = []
        for c in combat_side_one:
            initiative_sum, _ = roll_2d20()
            combat_side_one_initiative.append(initiative_sum + c.current_speed)
            if 0 in _:
                c.crit_fail = 1
            if 20 in _:
                c.crit_success = 1
            if 0 in _ and 20 in _:
                c.crit_fail = 0
                c.crit_success = 0
        # Side Two
        combat_side_two_initiative = []
        for c in combat_side_two:
            initiative_sum, _ = roll_2d20()
            combat_side_two_initiative.append(initiative_sum + c.current_speed)
            if 0 in _:
                c.crit_fail = 1
            if 20 in _:
                c.crit_success = 1
            if 0 in _ and 20 in _:
                c.crit_fail = 0
                c.crit_success = 0

        # Sort combat_side_one and combat_side_one_initiative by initiative (ascending)
        side_one_pairs = list(zip(combat_side_one_initiative, combat_side_one))
        side_one_pairs.sort(key=lambda x: x[0])
        combat_side_one_initiative, combat_side_one = zip(*side_one_pairs)
        combat_side_one_initiative = list(combat_side_one_initiative)
        combat_side_one = list(combat_side_one)

        # Sort combat_side_two and combat_side_two_initiative by initiative (ascending)
        side_two_pairs = list(zip(combat_side_two_initiative, combat_side_two))
        side_two_pairs.sort(key=lambda x: x[0])
        combat_side_two_initiative, combat_side_two = zip(*side_two_pairs)
        combat_side_two_initiative = list(combat_side_two_initiative)
        combat_side_two = list(combat_side_two)

        # Print initiative rolls for each character
        # print("Initiative Rolls:")
        # for idx, c in enumerate(combat_side_one):
            # print(f"  Side 1 - {c.name}: {combat_side_one_initiative[idx]}")
        # for idx, c in enumerate(combat_side_two):
            # print(f"  Side 2 - {c.name}: {combat_side_two_initiative[idx]}")

        # Check Initiative
        # Iterate Through Combat Side One
        i = 0
        while i < len(combat_side_one):
            c1 = combat_side_one[i]
            j = 0
            while j < len(combat_side_two):
                c2 = combat_side_two[j]
                # If Combatant Has Rolled Higher
                if ((combat_side_one_initiative[i] >= 30) and c1.currently_engaging == 0) or (combat_side_two[j].combatants_faced >= combat_side_two[j].max_combatants):
                    # Critical Strike
                    if (combat_side_one[i].crit_strike == 1):
                        if((combat_side_two_initiative[j].current_speed > combat_side_two_initiative[j].current_attack) and (combat_side_two_initiative[j].current_speed > combat_side_two_initiative[j].current_defense)):
                            combat_side_two[j].current_speed -= 2
                        elif((combat_side_two_initiative[j].current_attack > combat_side_two_initiative[j].current_speed) and (combat_side_two_initiative[j].current_attack > combat_side_two_initiative[j].current_defense)):
                            combat_side_two[j].current_attack -= 2
                        elif((combat_side_two_initiative[j].current_defense > combat_side_two_initiative[j].current_speed) and (combat_side_two_initiative[j].current_defense > combat_side_two_initiative[j].current_attack)):
                            combat_side_two[j].current_defense -= 2
                        critical_strike_injury = secondary_injury_roll(ct)
                        if isinstance(critical_strike_injury, str) and "Critical Injury" in critical_strike_injury:
                            combat_side_two.pop(i)
                            combat_side_two_initiative.pop(i)
                        if critical_strike_injury == "Major Injury":
                            combat_side_two[i].current_speed -= 2
                            combat_side_two[i].current_attack -= 2
                            combat_side_two[i].current_defense -= 2
                        if critical_strike_injury == "Minor Injury":
                            combat_side_two[i].current_speed -= 1
                            combat_side_two[i].current_attack -= 1
                            combat_side_two[i].current_defense -= 1
                        print(critical_strike_injury)
                    c1.currently_engaging = 1
                    c2.combatants_faced += 1
                    attack_sum, _ = roll_3d5()
                    attack_roll = ((attack_sum + c1.current_attack) - c2.current_defense)
                    c2.current_morale -= attack_roll
                    # print(f"{c2.name}'s Current Morale: {c2.current_morale}")
                    if (c2.current_morale <= 0) or (c2.current_morale <= c2.morale_threshold) or (len(c2.injuries) >= c2.injury_threshold):
                        # print(f"{combat_side_two[j].name} Defeated")
                        if(c2.current_morale <= 0):
                            morale_injury_roll = primary_injury_roll(ct)
                            print(morale_injury_roll)
                        combat_side_two.pop(j)
                        combat_side_two_initiative.pop(j)
                        continue  # Don't increment j, as list has shifted
                j += 1
            i += 1
            if (c1.currently_engaging == 0) and c1.crit_fail == 1:
                if((combat_side_one[i].current_speed > combat_side_one[i].current_attack) and (combat_side_one[i].current_speed > combat_side_one[i].current_defense)):
                    combat_side_one[i].current_speed -= 2
                elif((combat_side_one[i].current_attack > combat_side_one[i].current_speed) and (combat_side_one[i].current_attack > combat_side_one[i].current_defense)):
                    combat_side_one[i].current_attack -= 2
                elif((combat_side_one[i].current_defense > combat_side_one[i].current_speed) and (combat_side_one[i].current_defense > combat_side_one[i].current_attack)):
                    combat_side_one[i].current_defense -= 2
                critical_fail_injury = secondary_injury_roll(ct)
                if isinstance(critical_fail_injury, str) and "Critical Injury" in critical_fail_injury:
                    combat_side_one.pop(i)
                    combat_side_one_initiative.pop(i)
                if critical_fail_injury == "Major Injury":
                    combat_side_one[i].current_speed -= 2
                    combat_side_one[i].current_attack -= 2
                    combat_side_one[i].current_defense -= 2
                if critical_fail_injury == "Minor Injury":
                    combat_side_one[i].current_speed -= 1
                    combat_side_one[i].current_attack -= 1
                    combat_side_one[i].current_defense -= 1
                print(critical_fail_injury)

        # Iterate Through Combat Side Two
        i = 0
        while i < len(combat_side_two):
            c2 = combat_side_two[i]
            j = 0
            while j < len(combat_side_one):
                c1 = combat_side_one[j]
                # If Combatant Has Rolled Higher
                if ((combat_side_two_initiative[i] > 30) and c2.currently_engaging == 0) or (combat_side_one[j].combatants_faced >= combat_side_one[j].max_combatants):
                    # Critical Strike
                    if (combat_side_two[i].crit_strike == 1):
                        if((combat_side_one_initiative[j].current_speed > combat_side_one_initiative[j].current_attack) and (combat_side_one_initiative[j].current_speed > combat_side_one_initiative[j].current_defense)):
                            combat_side_one[j].current_speed -= 2
                        elif((combat_side_one_initiative[j].current_attack > combat_side_one_initiative[j].current_speed) and (combat_side_one_initiative[j].current_attack > combat_side_one_initiative[j].current_defense)):
                            combat_side_one[j].current_attack -= 2
                        elif((combat_side_one_initiative[j].current_defense > combat_side_one_initiative[j].current_speed) and (combat_side_one_initiative[j].current_defense > combat_side_one_initiative[j].current_attack)):
                            combat_side_one[j].current_defense -= 2
                        critical_strike_injury = secondary_injury_roll(ct)
                        if isinstance(critical_strike_injury, str) and "Critical Injury" in critical_strike_injury:
                            combat_side_one.pop(i)
                            combat_side_one_initiative.pop(i)
                        if critical_strike_injury == "Major Injury":
                            combat_side_one[i].current_speed -= 2
                            combat_side_one[i].current_attack -= 2
                            combat_side_one[i].current_defense -= 2
                        if critical_strike_injury == "Minor Injury":
                            combat_side_one[i].current_speed -= 1
                            combat_side_one[i].current_attack -= 1
                            combat_side_one[i].current_defense -= 1
                        print(critical_strike_injury)
                    # One Combatant Only
                    c2.currently_engaging = 1
                    c1.combatants_faced += 1
                    # Roll Attack
                    attack_sum, _ = roll_3d5()
                    attack_roll = ((attack_sum + c2.current_attack) - c1.current_defense)
                    c1.current_morale -= attack_roll
                    # print(f"{c1.name}'s Current Morale: {c1.current_morale}")
                    if (c1.current_morale <= 0) or (c1.current_morale <= c1.morale_threshold) or (len(c1.injuries) >= c1.injury_threshold):
                        # print(f"{combat_side_one[j].name} Defeated")
                        if(c1.current_morale <= 0):
                            morale_injury_roll = primary_injury_roll(ct)
                            print(morale_injury_roll)
                        combat_side_one.pop(j)
                        combat_side_one_initiative.pop(j)
                        continue  # Don't increment j, as list has shifted
                j += 1
            
            if (c2.currently_engaging == 0) and c2.crit_fail == 1:
                if((combat_side_two[i].current_speed > combat_side_two[i].current_attack) and (combat_side_two[i].current_speed > combat_side_two[i].current_defense)):
                    combat_side_two[i].current_speed -= 2
                elif((combat_side_two[i].current_attack > combat_side_two[i].current_speed) and (combat_side_two[i].current_attack > combat_side_two[i].current_defense)):
                    combat_side_two[i].current_attack -= 2
                elif((combat_side_two[i].current_defense > combat_side_two[i].current_speed) and (combat_side_two[i].current_defense > combat_side_two[i].current_attack)):
                    combat_side_two[i].current_defense -= 2
                critical_fail_injury = secondary_injury_roll(ct)
                if isinstance(critical_fail_injury, str) and "Critical Injury" in critical_fail_injury:
                    combat_side_two.pop(i)
                    combat_side_two_initiative.pop(i)
                if critical_fail_injury == "Major Injury":
                    combat_side_two[i].current_speed -= 2
                    combat_side_two[i].current_attack -= 2
                    combat_side_two[i].current_defense -= 2
                if critical_fail_injury == "Minor Injury":
                    combat_side_two[i].current_speed -= 1
                    combat_side_two[i].current_attack -= 1
                    combat_side_two[i].current_defense -= 1
                print(critical_fail_injury)
            i += 1
        
        # End Of Round
        # Stalemate
        stalemate = 1
        for c in combat_side_one:
            if c.currently_engaging == 1:
                stalemate = 0
        for c in combat_side_two:
            if c.currently_engaging == 1:
                stalemate = 0
        if stalemate == 1:
            print("This round has ended in a stalemate, neither side have made progress.")

        # End Of Round
        combat_side_one_initiative = []
        combat_side_two_initiative = []
        # Prepare For Next Round
        for c in combat_side_one:
            c.currently_engaging = 0
            c.crit_success = 0
            c.crit_fail = 0
            c.combatants_faced = 0
        # Prepare For Next Round
        for c in combat_side_two:
            c.currently_engaging = 0
            c.crit_success = 0
            c.crit_fail = 0
            c.combatants_faced = 0

    if len(combat_side_one) == 0:
        print("Side two wins the duel!")

    if len(combat_side_two) == 0:
        print("Side one wins the duel!")


######################################################################################################
# Combat Simulation
######################################################################################################

# Testing Block
# Characters
# arya = Character("Arya", 0, 0, 0, morale=50, age=18, perks=None, injuries=None, injury_threshold=4, morale_threshold=15)
# hound = Character("The Hound", 0, 0, 0, morale=50, age=18, perks=None, injuries=None, injury_threshold=4, morale_threshold=15)
# ygritte = Character("Ygritte", 0, 0, 0, morale=50, age=18, perks=None, injuries=None, injury_threshold=4, morale_threshold=15)
# jon = Character("Jon", 0, 0, 0, morale=50, age=18, perks=None, injuries=None, injury_threshold=4, morale_threshold=15)
# Sides
# side1 = [arya, hound]
# side2 = [ygritte, jon]

# Combat Initialization
def combat_initialization(combat_data, side1_data, side2_data):

    # Live Combat
    if combat_data == "Live Melee vs Melee":
        melee_melee(side1_data, side2_data, "steel")
    elif combat_data == "Live Ranged vs Melee":
        ranged_melee(side1_data, side2_data, "steel")
    elif combat_data == "Live Ranged vs Ranged":
        ranged_ranged(side1_data, side2_data, "steel")

    # Blunted Combat
    elif combat_data == "Blunted Melee vs Melee":
        melee_melee(side1_data, side2_data, "blunted")
    elif combat_data == "Blunted Ranged vs Melee":
        ranged_melee(side1_data, side2_data, "blunted")
    elif combat_data == "Blunted Ranged vs Ranged":
        ranged_ranged(side1_data, side2_data, "blunted")

######################################################################################################
# Maesty Interface
######################################################################################################

# Maesty Example Comments:

# Side 1: Arya, Brienne;
# Side 2: Jaime, Bronn;
# <Live Melee vs Melee>
# /u/maesterbot

# Side 1: Arya, Brienne;
# Side 2: Jaime, Bronn;
# <Live Ranged vs Melee>
# /u/maesterbot

# Side 1: Arya, Brienne;
# Side 2: Jaime, Bronn;
# <Live Ranged vs Ranged>
# /u/maesterbot

# Side 1: Arya, Brienne;
# Side 2: Jaime, Bronn;
# <Blunted Melee vs Melee>
# /u/maesterbot

# Side 1: Arya, Brienne;
# Side 2: Jaime, Bronn;
# <Blunted Ranged vs Melee>
# /u/maesterbot

# Side 1: Arya, Brienne;
# Side 2: Jaime, Bronn;
# <Blunted Ranged vs Ranged>
# /u/maesterbot

# Initial Data Required
# Side 1
side1_data = [
    {"name": "Arya", "age": 18, "perks": ["Born Lucky"], "injuries": [], "injury_threshold": 4, "morale_threshold": 15},
    {"name": "Brienne", "age": 32, "perks": ["Sworn Sword T2"], "injuries": [], "injury_threshold": 4, "morale_threshold": 15}
]
# Side 2
side2_data = [
    {"name": "Jaime", "age": 35, "perks": ["Blade Specialist T3"], "injuries": [], "injury_threshold": 4, "morale_threshold": 15},
    {"name": "Bronn", "age": 40, "perks": ["Marksman T1"], "injuries": [], "injury_threshold": 4, "morale_threshold": 15}
]

# Combat Type
# combat_data = "Live Melee vs Melee"
# combat_data = "Live Ranged vs Melee" - Side 1 Must Be Ranged
# combat_data = "Live Ranged vs Ranged"
# combat_data = "Blunted Melee vs Melee"
# combat_data = "Blunted Ranged vs Melee" - Side 1 Must Be Ranged
# combat_data = "Blunted Ranged vs Ranged"

# Combat Initialization
if __name__ == "__main__":
    # combat_data = "Live Melee vs Melee"                                 # Example Combat Type
    combat_data = "Live Melee vs Melee"
    combat_initialization(combat_data, side1_data, side2_data)          # Initialize Combat

    # Pause at the end so output is visible if run from double-click or IDE
    input("\nPress Enter to exit...")

######################################################################################################
# CLI Interface
######################################################################################################


