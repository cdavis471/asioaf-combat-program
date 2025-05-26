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

    # Weapon Specialist Trees
    "Blade Specialist T1": {"melee": {"speed": 1, "attack": 1, "defense": 0}},
    "Blade Specialist T2": {"melee": {"speed": 2, "attack": 1, "defense": 1}},
    "Blade Specialist T3": {"melee": {"speed": 2, "attack": 2, "defense": 2}},
    "Axe and Blunt Specialist T1": {"melee": {"speed": 1, "attack": 1, "defense": 0}},
    "Axe and Blunt Specialist T2": {"melee": {"speed": 2, "attack": 2, "defense": 0}},
    "Axe and Blunt Specialist T3": {"melee": {"speed": 2, "attack": 3, "defense": 1}},
    "Spear Specialist T1": {"melee": {"speed": 1, "attack": 0, "defense": 1}},
    "Spear Specialist T2": {"melee": {"speed": 2, "attack": 1, "defense": 1}},
    "Spear Specialist T3": {"melee": {"speed": 3, "attack": 1, "defense": 2}},

    # Duelist Tree
    "Duelist T1": {"melee": {"speed": 2, "attack": 0, "defense": 0}},
    "Duelist T2": {"melee": {"speed": 4, "attack": 0, "defense": 0}},
    "Duelist T3": {"melee": {"speed": 5, "attack": 0, "defense": 0}},

    # Shield Specialist
    "Shield Specialist T1": {"melee": {"speed": 0, "attack": 0, "defense": 2}, "ranged": {"speed": 0, "attack": 0, "defense": 1}},
    "Shield Specialist T2": {"melee": {"speed": 0, "attack": 0, "defense": 4}, "ranged": {"speed": 0, "attack": 0, "defense": 2}},
    "Shield Specialist T3": {"melee": {"speed": 0, "attack": 0, "defense": 6}, "ranged": {"speed": 0, "attack": 0, "defense": 3}},

    # Steel Tempest
    "Steel Tempest T1": {"melee": {"speed": 0, "attack": 1, "defense": 1}},
    "Steel Tempest T2": {"melee": {"speed": 0, "attack": 2, "defense": 2}},
    "Steel Tempest T3": {"melee": {"speed": 0, "attack": 3, "defense": 3}},

    # Sworn Sword
    "Sworn Sword T1": {"melee": {"speed": 1, "attack": 0, "defense": 1}},
    "Sworn Sword T2": {"melee": {"speed": 2, "attack": 0, "defense": 2}},
    "Sworn Sword T3": {"melee": {"speed": 3, "attack": 0, "defense": 3}},

    # Battlefield Champion
    "Battlefield Champion T1": {"all": {"speed": 1, "attack": 1, "defense": 0}},
    "Battlefield Champion T2": {"all": {"speed": 2, "attack": 2, "defense": 0}},
    "Battlefield Champion T3": {"all": {"speed": 3, "attack": 3, "defense": 0}},

    # Ranged Specialist
    "Bow Specialist T1": {"ranged": {"speed": 2, "attack": 1, "defense": 0}},
    "Bow Specialist T2": {"ranged": {"speed": 3, "attack": 2, "defense": 0}},
    "Bow Specialist T3": {"ranged": {"speed": 4, "attack": 3, "defense": 0}},
    "Crossbow Specialist T1": {"ranged": {"speed": 1, "attack": 2, "defense": 0}},
    "Crossbow Specialist T2": {"ranged": {"speed": 2, "attack": 4, "defense": 0}},
    "Crossbow Specialist T3": {"ranged": {"speed": 3, "attack": 5, "defense": 0}},

    # Marksman
    "Marksman T1": {"ranged": {"speed": 2, "attack": 0, "defense": 0}},
    "Marksman T2": {"ranged": {"speed": 4, "attack": 0, "defense": 0}},
    "Marksman T3": {"ranged": {"speed": 6, "attack": 1, "defense": 0}},

    # Projectile Specialist
    "Thrown Projectile Specialist T1": {"all": {"speed": 1, "attack": 0, "defense": 0}},
    "Thrown Projectile Specialist T2": {"all": {"speed": 2, "attack": 0, "defense": 0}},
    "Thrown Projectile Specialist T3": {"all": {"speed": 3, "attack": 1, "defense": 0}},

    # Special Prowess Perks
    "Bloodlust": {"melee": {"speed": 0, "attack": 0, "defense": 2}},
    "Berserker": {"melee": {"speed": 0, "attack": 2, "defense": 0}},
    "First in the Fray": {"all": {"speed": 1, "attack": 1, "defense": 1}},
    "Born Lucky": {"all": {"speed": 1, "attack": 0, "defense": 0}},
    "Favored by Fortune": {"all": {"speed": 0, "attack": 0, "defense": 2}}

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
            return "Critical Injury"                        # ---- Critical Injury
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
            return "Critical Injury"                        # ---- Critical Injury
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
    result = roll_1d100()
    if character.perks:
        for perk in character.perks:
            if perk == "Battlefield Champion T1":
                result += 5
            elif perk == "Battlefield Champion T2":
                result += 10
            elif perk == "Indomitable T1":
                result += 5
            elif perk == "Indomitable T2":
                result += 10
            elif perk == "Indomitable T3":
                result += 15
            elif perk == "Duelist T1":
                result += 5
            elif perk == "Duelist T2":
                result += 10
            elif perk == "Command & Presence":
                result += 10
    if result > 50:
        return "Character Finds Opponent!"
    else:
        return "Character Fails To Find Opponent!"
    
def side_initialization(side_data):
    side = []
    for spec in side_data:
        char = Character(
            spec["name"],                          
            age=spec["age"],
            perks=spec.get("perks", []),
            injuries=spec.get("injuries", []),
            injury_threshold=spec.get("injury_threshold", 4),
            morale_threshold=spec.get("morale_threshold", 15)
        )
        side.append(char)
    return side

# Melee vs Melee - Live
def live_melee_melee(side1, side2):
    # Initialize Sides
    combat_side_one = side_initialization(side1)
    combat_side_two = side_initialization(side2)

    # Initialize Characters
    for i in range(len(combat_side_one)):
        melee_initialization(combat_side_one[i])
    for j in range(len(combat_side_two)):
        melee_initialization(combat_side_two[j])

    # Melee vs Melee Combat

# Ranged vs Melee - Live
def live_ranged_melee(side1, side2):
    # Initialize Sides
    combat_side_one = side_initialization(side1)
    combat_side_two = side_initialization(side2)

    # Initialize Characters
    for i in range(len(combat_side_one)):
        ranged_initialization(combat_side_one[i])
    for j in range(len(combat_side_two)):
        melee_initialization(combat_side_two[j])

    # Ranged vs Melee Combat


    # Melee vs Melee Combat
    for i in range(len(combat_side_one)):
        mixed_initialization(combat_side_one[i])

# Ranged vs Ranged - Live
def live_ranged_ranged(side1, side2):
    # Initialize Sides
    combat_side_one = side_initialization(side1)
    combat_side_two = side_initialization(side2)

    # Initialize Characters
    for i in range(len(combat_side_one)):
        ranged_initialization(combat_side_one[i])
    for j in range(len(combat_side_two)):
        ranged_initialization(combat_side_one[j])

    # Ranged vs Ranged Combat

# Melee vs Melee - Blunted
def blunted_melee_melee(side1, side2):
    # Initialize Sides
    combat_side_one = side_initialization(side1)
    combat_side_two = side_initialization(side2)
    # Initialize Characters
    for i in range(len(combat_side_one)):
        melee_initialization(combat_side_one[i])
    for j in range(len(combat_side_two)):
        melee_initialization(combat_side_two[j])

# Ranged vs Melee - Blunted
def blunted_ranged_melee(side1, side2):
    # Initialize Sides
    combat_side_one = side_initialization(side1)
    combat_side_two = side_initialization(side2)
    # Initialize Characters
    for i in range(len(combat_side_one)):
        ranged_initialization(combat_side_one[i])
    for j in range(len(combat_side_two)):
        melee_initialization(combat_side_two[j])

    # Melee vs Melee Phase
    for i in range(len(combat_side_one)):
        mixed_initialization(combat_side_one[i])

# Ranged vs Ranged - Blunted
def blunted_ranged_ranged(side1, side2):
    # Initialize Sides
    combat_side_one = side_initialization(side1)
    combat_side_two = side_initialization(side2)
    # Initialize Characters
    for i in range(len(combat_side_one)):
        ranged_initialization(combat_side_one[i])
    for j in range(len(combat_side_two)):
        ranged_initialization(combat_side_one[j])

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
        live_melee_melee(side1_data, side2_data)
    elif combat_data == "Live Ranged vs Melee":
        live_ranged_melee(side1_data, side2_data)
    elif combat_data == "Live Ranged vs Ranged":
        live_ranged_ranged(side1_data, side2_data)

    # Blunted Combat
    elif combat_data == "Blunted Melee vs Melee":
        blunted_melee_melee(side1_data, side2_data)
    elif combat_data == "Blunted Ranged vs Melee":
        blunted_ranged_melee(side1_data, side2_data)
    elif combat_data == "Blunted Ranged vs Ranged":
        blunted_ranged_ranged(side1_data, side2_data)

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
combat_data = "Live Melee vs Melee"                                 # Example Combat Type
combat_initialization(combat_data, side1_data, side2_data)          # Initialize Combat

######################################################################################################
# CLI Interface
######################################################################################################


