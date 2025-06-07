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
    def __init__(self, name, age=18, perks=None, injuries=None, injury_threshold=4, morale_threshold=15, items=None):

        # Base Stats
        self.name = name                            # Character Name
        self.age = age                              # Character Age
        self.perks = perks or []                    # Character Perks
        self.injuries = injuries or []              # Character Injuries
        self.injury_threshold = injury_threshold    # Injury Threshold
        self.morale_threshold = morale_threshold    # Morale Threshold
        self.items = items or []                    # Character Items

        # Dynamic Stats
        self.current_speed = 0                      # Current Speed
        self.current_attack = 0                     # Current Attack
        self.current_defense = 0                    # Current Defense
        self.current_morale = 50                    # Current Morale

        # Perk Check
        self.max_combatants = 3                     # Max Combatants Before Free Attack
        self.max_mixed_rounds = 2                   # Max Mixed Rounds (Ranged to Melee)
        self.major_injury_buff = 0                  # Indomitable Perk Check
        self.you_lucky = 0                          # Born Lucky Perk Check
        self.bloodlusted = 0                        # Blood Lust Perk Check
        self.imposed_presence = 0                   # Terrifying Presence T1 & T2 Check
        self.berserked = 0                          # Berserker Perk Check

        # Combat Checks
        self.currently_engaging = 0                 # Attacking Someone This Round
        self.crit_success = 0                        # Crit Strike Rolled
        self.crit_fail = 0                          # Crit Fail Rolled
        self.combatants_faced = 0                   # Combatants Faced
        self.major_injuries = 0                     # Major Injuries Taken

######################################################################################################
# Age Malus
######################################################################################################

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

######################################################################################################
# Perk Stats
######################################################################################################
 
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
    "Favored by Fortune": {"all": {"speed": 0, "attack": 0, "defense": 2}}                    # Favored by Fortune

}

######################################################################################################
# Initialize Melee Stats
######################################################################################################

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
                character.max_combatants += 1                                           # ---- Max Combatants +1
                character.major_injury_buff += 1                                        # ---- Ignore 1 Major Injury
            
            if perk == "Indomitable T2":                                                # --- If Perk - Indomitable T1
                character.current_morale += 30                                          # ---- +30 Morale
                character.max_combatants += 2                                           # ---- Max Combatants +2
                character.major_injury_buff += 2                                        # ---- Ignore 2 Major Injuries

            if perk == "Indomitable T3":                                                # --- If Perk - Indomitable T1
                character.current_morale += 45                                          # ---- +45 Morale
                character.max_combatants += 3                                           # ---- Max Combatants +3
                character.major_injury_buff += 3                                        # ---- Ignore 3 Major Injuries
                                         

    # Apply Item Modifiers
    if character.items:
        for item in character.items:
            if item == "Castle-Forged Weapon":
                character.current_attack += 1
            if item == "Castle-Forged Plate":
                character.current_defense += 1
            if item == "Masterwork Weapon":
                character.current_attack += 2
            if item == "Ornate Platemail":
                character.current_defense += 2
            if item == "Qohorik Steel Weapon":
                character.current_attack += 3
            if item == "Qohorik Armor":
                character.current_defense += 3
            if item == "Valyrian Steel Weapon":
                character.current_attack += 4
            if item == "Valyrian Steel Armor":
                character.current_defense += 4
    
    # Apply Current Injury Debuffs
    if character.injuries:
        if len(character.injuries) == 1:
            character.current_speed -= character.injuries[0]
        
        if len(character.injuries) == 2:
            character.current_speed -= character.injuries[0]
            character.current_attack -= character.injuries[1]

        if len(character.injuries) == 3:
            character.current_speed -= character.injuries[0]
            character.current_attack -= character.injuries[1]
            character.current_defense -= character.injuries[2]

######################################################################################################
# Initialize Ranged Stats
######################################################################################################

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

            if perk == "Marksman T3":                                                   # --- If Perk - Marksman T3
                character.max_mixed_rounds += 1                                         # ---- Extra Mixed Combat Round

    # Apply Item Modifiers
    if character.items:
        for item in character.items:
            if item == "Fine-Strung Bow":
                character.current_attack += 1
            if item == "Goldenheart Bow":
                character.current_attack += 2
            if item == "Dragonbone Bow":
                character.current_attack += 3
            if item == "Castle-Forged Plate":
                character.current_defense += 1
            if item == "Ornate Platemail":
                character.current_defense += 2
            if item == "Qohorik Armor":
                character.current_defense += 3
            if item == "Valyrian Steel Armor":
                character.current_defense += 4
    
    # Apply Current Injury Debuffs
    if character.injuries:
        if len(character.injuries) == 1:
            character.current_speed -= character.injuries[0]
        
        if len(character.injuries) == 2:
            character.current_speed -= character.injuries[0]
            character.current_attack -= character.injuries[1]

        if len(character.injuries) == 3:
            character.current_speed -= character.injuries[0]
            character.current_attack -= character.injuries[1]
            character.current_defense -= character.injuries[2]
            
######################################################################################################
# Initialize Mixed Stats
######################################################################################################

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

            if perk == "Indomitable T1":                                                # --- If Perk - Indomitable T1
                character.current_morale += 15                                          # ---- Morale: 65
                character.max_combatants = 4                                            # ---- Max Combatants +1
            
            if perk == "Indomitable T2":                                                # --- If Perk - Indomitable T1
                character.current_morale += 30                                          # ---- Morale: 80
                character.max_combatants = 5                                            # ---- Max Combatants +2

            if perk == "Indomitable T3":                                                # --- If Perk - Indomitable T1
                character.current_morale += 45                                          # ---- Morale: 95
                character.max_combatants = 6                                            # ---- Max Combatants +3

    # Apply Item Modifiers
    if character.items:                                                                 # - If Character Has Items
        for item in character.items:                                                    # -- For Each Item
            if item == "Fine-Strung Bow":                                               # --- If Fine-Strung Bow
                character.current_attack -= 1                                           # ---- Remove Previous Modifier
            if item == "Goldenheart Bow":                                               # --- If Goldeheart Bow
                character.current_attack -= 2                                           # ---- Remove Previous Modifier
            if item == "Dragonbone Bow":                                                # --- If Dragonbone Bow
                character.current_attack -= 3                                           # ---- Remove Previous Modifier
            if item == "Castle-Forged Weapon":                                          # --- If Castle-Forged Weapon
                character.current_attack += 1                                           # ---- Add New Modifier
            if item == "Masterwork Weapon":                                             # --- If Masterwork Weapon
                character.current_attack += 2                                           # ---- Add New Modifier
            if item == "Qohorik Steel Weapon":                                          # --- If Qohorik Steel Weapon
                character.current_attack += 3                                           # ---- Add New Modifier
            if item == "Valyrian Steel Weapon":
                character.current_attack += 4

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

def primary_injury_roll(weapons, bonus):                           
    """Roll for Primary Injury - 1d100"""                    
    roll = roll_1d100()                                     # - Roll 1d100     
    roll = roll + bonus                                     # - Add Bonus (If Any)
    if weapons.lower() == "steel":                          # -- Live Steel
        if 1 <= roll <= 25:                                 # --- 1-25    
            return "Death"                                  # ---- Death
        elif 26 <= roll <= 40:                              # --- 26-40
            crit = critical_injury()                        # ---- Roll Critical Injury
            return f"{crit}"                                # ---- Critical Injury
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
    
def secondary_injury_roll(weapons, bonus):                          
    """Roll for Secondary Injury - 1d100"""                  
    roll = roll_1d100()                                     # - Roll 1d100   
    roll = roll + bonus                                     # - Add Bonus (If Any)
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
# Battlefield Duel Seeking
######################################################################################################

# Battlefield Duel Seeking
def combat_seeking(target, seeker):
    result = roll_1d100()                                           # - Roll D100
    if seeker.perks:                                                # - Character Perk Bonuses
        for perk in seeker.perks:                                   # -- Iterate Through Perks
            if perk == "Battlefield Champion T3":                   # --- Battlefield Champion T1
                result += 5                                         # ---- Add 5
            elif perk == "Battlefield Champion T2":                 # --- Battlefield Champion T2
                result += 5                                         # ---- Add 10
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
    
######################################################################################################
# Side Initialization
######################################################################################################

# Side Initialization
def side_initialization(side_data):
    side = []
    for spec in side_data:
        # Defensive: skip empty dicts or missing name
        if not spec or not spec.get("name"):
            continue
        # Ensure injuries are integers (maluses), not strings
        injuries = spec.get("injuries", [])
        # Convert to int if not already
        injuries = [int(i) if str(i).strip() != "" else 0 for i in injuries]
        # Pad to 3 values if needed
        while len(injuries) < 3:
            injuries.append(0)
        char = Character(
            spec["name"],
            age=spec.get("age", 18),
            perks=spec.get("perks", []),
            injuries=injuries,
            injury_threshold=spec.get("injury_threshold", 4),
            morale_threshold=spec.get("morale_threshold", 15),
            items=spec.get("items", [])
        )
        side.append(char)
    return side

######################################################################################################
# Side Initialization
######################################################################################################

def combat_log_string(combat_log):
    for entry in combat_log:
        print(entry)

######################################################################################################
# Combat Scenario - Melee vs Melee
######################################################################################################

def melee_melee(side1, side2, ct):

    # Combat Log
    combat_log = []
    round_count = 0   

    # Side Initialization
    combat_side_one = side_initialization(side1)
    combat_side_two = side_initialization(side2)
    # Stat Initialization
    for c in combat_side_one + combat_side_two:
        melee_initialization(c)

    # Log fighters and their teams before combat starts
    combat_log.append("==============================================================")
    if not combat_log:
        combat_log.append("Side 1")
        for c in combat_side_one:
            combat_log.append(
                f"  {c.name} - Speed: {c.current_speed} | Attack: {c.current_attack} | Defense: {c.current_defense} | Morale: {c.current_morale} | Perks: {c.perks} | Injury Malus: {c.injuries} | Items: {c.items}"
            )
        combat_log.append("Side 2")
        for c in combat_side_two:
            combat_log.append(
                f"  {c.name} - Speed: {c.current_speed} | Attack: {c.current_attack} | Defense: {c.current_defense} | Morale: {c.current_morale} | Perks: {c.perks} | Injury Malus: {c.injuries} | Items: {c.items}"
            )
    combat_log.append("==============================================================")

    # Battlefield Champion T3 Check
    # Side One
    bc3_count = 0
    bc3_check = 0
    for c in combat_side_one:
        if "Battlefield Champion T3" in c.perks:
            for d in combat_side_one:
                if(bc3_count != bc3_check):
                    d.current_morale += 7
                bc3_check +=1
            combat_log.append(f"The presence of the Battlefield Champion {c.name} boosts the morale of the men around them!")
        bc3_count += 1

    # Side Two
    bc3_count = 0
    bc3_check = 0
    for e in combat_side_two:
        if "Battlefield Champion T3" in e.perks:
            for f in combat_side_one:
                if(bc3_count != bc3_check):
                    f.current_morale += 7
                bc3_check +=1
            combat_log.append(f"The presence of the Battlefield Champion {e.name} boosts the morale of the men around them!")
        bc3_count += 1

    # While Both Teams Have Combatants
    while len(combat_side_one) > 0 and len(combat_side_two) > 0:

        round_count += 1
        combat_log.append("==============================================================")

        # Terrifying Presence T1 Check
        # Side One
        if (len(combat_side_one) == 1) and len(combat_side_two) > 1 and ("Terrifying Presence T1" in combat_side_one[0].perks) and (combat_side_one[0].imposed_presence == 0):
            combat_side_one[0].imposed_presence = 1
            for c in combat_side_two:
                c.morale_threshold += 10
            combat_log.append(f"The terrifying presence of {combat_side_one[0].name} strikes fear into the heart of their enemies!")
        # Side Two
        if (len(combat_side_two) == 1) and len(combat_side_one) > 1 and ("Terrifying Presence T1" in combat_side_two[0].perks) and (combat_side_two[0].imposed_presence == 0):
            combat_side_two[0].imposed_presence = 1
            for c in combat_side_one:
                c.morale_threshold += 10
            combat_log.append(f"The terrifying presence of {combat_side_two[0].name} strikes fear into the heart of their enemies!")
        # Terrifying Presence T2 Check
        # Side One
        if (len(combat_side_one) == 1) and len(combat_side_two) > 1 and ("Terrifying Presence T2" in combat_side_one[0].perks) and (combat_side_one[0].imposed_presence == 0):
            combat_side_one[0].imposed_presence = 1
            for c in combat_side_two:
                c.morale_threshold += 15
            combat_log.append(f"The terrifying presence of {combat_side_one[0].name} strikes fear into the heart of their enemies!")
        # Side Two
        if (len(combat_side_two) == 1) and len(combat_side_one) > 1 and ("Terrifying Presence T2" in combat_side_two[0].perks) and (combat_side_two[0].imposed_presence == 0):
            combat_side_two[0].imposed_presence = 1
            for c in combat_side_one:
                c.morale_threshold += 15
            combat_log.append(f"The terrifying presence of {combat_side_two[0].name} strikes fear into the heart of their enemies!")
        # Roll Initiative
        # Side One
        combat_side_one_initiative = []
        for c in combat_side_one:
            initiative_sum, _ = roll_2d20()
            combat_log.append(f"{c.name} rolls initiative: {_} + Speed {c.current_speed} = {initiative_sum + c.current_speed}")
            # Born Lucky Perk Check
            if ("Born Lucky" in c.perks) and (1 in _) and c.you_lucky == 0:
                c.you_lucky = 1
                initiative_sum, _ = roll_2d20()
                combat_log.append(f"{c.name} is lucky! They re-roll their initiative: {initiative_sum} + Speed {c.current_speed} = {initiative_sum + c.current_speed}")
            combat_side_one_initiative.append(initiative_sum + c.current_speed)
            # Combat Log
            # Crit Checks
            if 1 in _:
                c.crit_fail = 1
                combat_log.append(f"{c.name} rolls a Critical Fail!")
            if 20 in _:
                c.crit_success = 1
                combat_log.append(f"{c.name} rolls a Critical Success!")
            if 19 in _ and "Duelist T3" in c.perks:
                c.crit_success = 1
                combat_log.append(f"{c.name} rolls a Critical Success!")
            if 1 in _ and 20 in _:
                c.crit_fail = 0
                c.crit_success = 0
            # Thrown Projectile Specialist T3 - Free Throw
            if initiative_sum >= 30 and "Thrown Projectile Specialist T3" in c.perks and round_count == 1:
                # Random Target Chosen
                target = random.sample(combat_side_two, 1)[0]
                target_index = combat_side_two.index(target)
                combat_log.append(f"{c.name} throws a projectile at {target.name}")
                # Critical Strike
                if (c.crit_success == 1):
                    # Speed Highest
                    if((target.current_speed > target.current_attack) and (target.current_speed > target.current_defense)):
                        target.current_speed -= 2
                    # Attack Highest
                    elif((target.current_attack > target.current_speed) and (target.current_attack > target.current_defense)):
                        target.current_attack -= 2
                    # defense Highest
                    elif((target.current_defense > target.current_speed) and (target.current_defense > target.current_attack)):
                        target.current_defense -= 2
                    bonus = 0
                    if "Sworn Sword T1" in target.perks:
                        bonus += 10
                    if "Sworn Sword T2" in target.perks:
                        bonus += 20
                    if "Sworn Sword T2" in target.perks:
                        bonus += 30
                    critical_strike_injury = secondary_injury_roll(ct, bonus)
                    # Critical Injury
                    if isinstance(critical_strike_injury, str) and "Critical Injury" in critical_strike_injury:
                        combat_log.append(f"{target.name} suffers {critical_strike_injury} and is taken out!")
                        combat_side_two.pop(target_index)
                        continue
                    # Major Injury
                    if critical_strike_injury == "Major Injury":
                        if "Ageing With Grace" in target.perks:
                            target.current_speed -= 1
                            target.current_attack -= 1
                            target.current_defense -= 1
                        else:
                            target.current_speed -= 2
                            target.current_attack -= 2
                            target.current_defense -= 2
                    # Minor Injury
                    if critical_strike_injury == "Minor Injury":
                        if "Bloodlust" in target.perks and target.bloodlusted == 0:
                            target.current_speed += 2
                            target.current_attack += 2
                            target.bloodlusted = 1
                        else:
                            target.current_speed -= 1
                            target.current_attack -= 1
                            target.current_defense -= 1
                    combat_log.append(f"{target.name} suffers {critical_strike_injury}")
                    combat_log.append(f"{target.name} Current Status - Speed: {target.current_speed} | Attack: {target.current_attack} | Defense: {target.current_defense}")
                # Status Checks
                c.currently_engaging = 1
                target.combatants_faced += 1
                # Attack Roll
                attack_sum, _ = roll_3d5()
                attack_roll = ((attack_sum + c.current_attack) - target.current_defense)
                # Steel Tempest Perk Check
                if "Steel Tempest T3" in c.perks:
                    attack_roll = (attack_roll*2)
                # Minimum Attack - 1
                if attack_roll <= 0:
                    attack_roll = 1
                # Deduct From Morale
                target.current_morale -= attack_roll
                combat_log.append(f"{c.name} attacks {target.name} → Roll: {attack_sum} + Attack {c.current_attack} - Defense {target.current_defense} = {attack_roll}")
                combat_log.append(f"{target.name}'s morale drops to {target.current_morale}")
                combat_log.append(f"{target.name} Current Status - Speed: {target.current_speed} | Attack: {target.current_attack} | Defense: {target.current_defense}")
                # Activate Berserker Rage Perk
                if ((target.current_morale <= 0) or (target.current_morale <= target.morale_threshold)) and "Berserker" in target.perks and target.berserked == 0:
                    target.current_morale += attack_roll
                    target.current_morale = (target.current_morale * 2)
                    target.berserked = 1
                    combat_log.append(f"{target.name} has gone berserk! Their morale has returned to: {target.current_morale}")
                # Duel End
                if (target.current_morale <= 0) or (target.current_morale <= target.morale_threshold) or (len(target.injuries) >= target.injury_threshold):
                    # If Below Morale
                    combat_log.append(f"{target.name} has been defeated!")
                    if(target.current_morale <= 0):
                        # Roll Primary Injury
                        bonus = 0
                        if "Sworn Sword T1" in target.perks:
                            bonus += 10
                        if "Sworn Sword T2" in target.perks:
                            bonus += 20
                        if "Sworn Sword T2" in target.perks:
                            bonus += 30
                        morale_injury_roll = primary_injury_roll(ct, bonus)
                        combat_log.append(f"{target.name} has been injured! - {morale_injury_roll}!")
                    combat_side_two.pop(target_index)
                # If Terrifying Presence - Only Take One Hit
                if ("Terrifying Presence T2" in target.perks) and (target.combatants_faced >= 1) and (len(combat_side_two)) == 1:
                    continue
            # Crit Fail & Missed Opponents
            if ((c.currently_engaging == 0) and c.crit_fail == 1) and initiative_sum < 30 and "Thrown Projectile Specialist T3" in c.perks and round_count == 1:
                # Speed Highest
                if((c.current_speed > c.current_attack) and (c.current_speed > c.current_defense)):
                    c.current_speed -= 2
                # Attack Highest
                elif((c.current_attack > c.current_speed) and (c.current_attack > c.current_defense)):
                    c.current_attack -= 2
                # defense Highest
                elif((c.current_defense > c.current_speed) and (c.current_defense > c.current_attack)):
                    c.current_defense -= 2
                bonus = 0
                if "Sworn Sword T1" in c.perks:
                    bonus += 10
                if "Sworn Sword T2" in c.perks:
                    bonus += 20
                if "Sworn Sword T2" in c.perks:
                    bonus += 30
                critical_fail_injury = secondary_injury_roll(ct, bonus)
                # Critical Injury
                if isinstance(critical_fail_injury, str) and "Critical Injury" in critical_fail_injury:
                    combat_log.append(f"{c.name} suffers {critical_fail_injury} and is taken out!")
                    combat_side_one.pop(c)
                # Major Injury
                if critical_fail_injury == "Major Injury":
                    if "Ageing With Grace" in c.perks:
                        c.current_speed -= 1
                        c.current_attack -= 1
                        c.current_defense -= 1
                    else:
                        c.current_speed -= 2
                        c.current_attack -= 2
                        c.current_defense -= 2
                # Minor Injury
                if critical_fail_injury == "Minor Injury":
                    c.current_speed -= 1
                    c.current_attack -= 1
                    c.current_defense -= 1
                combat_log.append(f"{c.name} suffers {critical_fail_injury}")
                combat_log.append(f"{c.name} Current Status - Speed: {c.current_speed} | Attack: {c.current_attack} | Defense: {c.current_defense}")

        # Side Two
        combat_side_two_initiative = []
        for c in combat_side_two:
            initiative_sum, _ = roll_2d20()
            combat_log.append(f"{c.name} rolls initiative: {_} + Speed {c.current_speed} = {initiative_sum + c.current_speed}")
            # Born Lucky Perk Check
            if ("Born Lucky" in c.perks) and (1 in _) and c.you_lucky == 0:
                c.you_lucky = 1
                initiative_sum, _ = roll_2d20()
                combat_log.append(f"{c.name} is lucky! They re-roll their initiative: {initiative_sum} + Speed {c.current_speed} = {initiative_sum + c.current_speed}")
            combat_side_two_initiative.append(initiative_sum + c.current_speed)
            # Crit Checks
            if 1 in _:
                c.crit_fail = 1
                combat_log.append(f"{c.name} rolls a Critical Fail!")
            if 20 in _:
                c.crit_success = 1
                combat_log.append(f"{c.name} rolls a Critical Success!")
            if 19 in _ and "Duelist T3" in c.perks:
                c.crit_success = 1
                combat_log.append(f"{c.name} rolls a Critical Success!")
            if 1 in _ and 20 in _:
                c.crit_fail = 0
                c.crit_success = 0
            # Thrown Projectile Specialist T3 - Free Throw
            if initiative_sum >= 30 and "Thrown Projectile Specialist T3" in c.perks and round_count == 1:
                # Random Target
                target = random.sample(combat_side_one, 1)[0]
                target_index = combat_side_one.index(target)
                combat_log.append(f"{c.name} throws a projectile at {target.name}")
                # Critical Strike
                if (c.crit_success == 1):
                    # Highest Speed
                    if((target.current_speed > target.current_attack) and (target.current_speed > target.current_defense)):
                        target.current_speed -= 2
                    # Highest Attack
                    elif((target.current_attack > target.current_speed) and (target.current_attack > target.current_defense)):
                        target.current_attack -= 2
                    # Highest Defense
                    elif((target.current_defense > target.current_speed) and (target.current_defense > target.current_attack)):
                        target.current_defense -= 2
                    bonus = 0
                    if "Sworn Sword T1" in target.perks:
                        bonus += 10
                    if "Sworn Sword T2" in target.perks:
                        bonus += 20
                    if "Sworn Sword T2" in target.perks:
                        bonus += 30
                    critical_strike_injury = secondary_injury_roll(ct, bonus)
                    # Critical Injury
                    if isinstance(critical_strike_injury, str) and "Critical Injury" in critical_strike_injury:
                        combat_log.append(f"{c.name} suffers {critical_strike_injury} and is taken out!")
                        combat_side_one.pop(target_index)
                        continue
                    # Major Injury
                    if critical_strike_injury == "Major Injury":
                        if "Ageing With Grace" in target.perks:
                            target.current_speed -= 1
                            target.current_attack -= 1
                            target.current_defense -= 1
                        else:
                            target.current_speed -= 2
                            target.current_attack -= 2
                            target.current_defense -= 2
                    # Minor Injury
                    if critical_strike_injury == "Minor Injury":
                        if "Bloodlust" in target.perks and target.bloodlusted == 0:
                            target.current_speed += 2
                            target.current_attack += 2
                            target.bloodlusted = 1
                        else:
                            target.current_speed -= 1
                            target.current_attack -= 1
                            target.current_defense -= 1
                    combat_log.append(f"{target.name} suffers {critical_strike_injury}")
                    combat_log.append(f"{target.name} Current Status - Speed: {target.current_speed} | Attack: {target.current_attack} | Defense: {target.current_defense}")
                # Status Check
                c.currently_engaging = 1
                target.combatants_faced += 1
                # Attack Roll
                attack_sum, _ = roll_3d5()
                attack_roll = ((attack_sum + c.current_attack) - target.current_defense)
                # Steel Tempest T3 - Double Attack
                if "Steel Tempest T3" in c.perks:
                    attack_roll = attack_roll * 2
                # Minimum Attack Roll - 1
                if attack_roll <= 0:
                    attack_roll = 1
                # Deduct from Target Morale
                target.current_morale -= attack_roll
                combat_log.append(f"{c.name} attacks {target.name} → Roll: {attack_sum} + Attack {c.current_attack} - Defense {target.current_defense} = {attack_roll}")
                combat_log.append(f"{target.name}'s morale drops to {target.current_morale}")
                combat_log.append(f"{target.name} Current Status - Speed: {target.current_speed} | Attack: {target.current_attack} | Defense: {target.current_defense}")
                # Berserker Rage Activated
                if ((target.current_morale <= 0) or (target.current_morale <= target.morale_threshold)) and "Berserker" in target.perks and target.berserked == 0:
                    target.current_morale += attack_roll
                    target.current_morale = (target.current_morale * 2)
                    target.berserked = 1
                    combat_log.append(f"{target.name} has gone berserk! Their morale has returned to: {target.current_morale}")
                # Target Knocked Out
                if (target.current_morale <= 0) or (target.current_morale <= target.morale_threshold) or (len(target.injuries) >= target.injury_threshold):
                    combat_log.append(f"{target.name} has been defeated!")
                    if(target.current_morale <= 0):
                        # Roll Primary Injury
                        bonus = 0
                        if "Sworn Sword T1" in target.perks:
                            bonus += 10
                        if "Sworn Sword T2" in target.perks:
                            bonus += 20
                        if "Sworn Sword T2" in target.perks:
                            bonus += 30
                        morale_injury_roll = primary_injury_roll(ct, bonus)
                        combat_log.append(f"{target.name} has been injured! - {morale_injury_roll}!")
                    combat_side_one.pop(target_index)
                # Terrifying Presence - Face One Opponent
                if ("Terrifying Presence T2" in target.perks) and (target.combatants_faced >= 1) and (len(combat_side_one)) == 1:
                    continue
            # Crit Fail & Miss
            if ((c.currently_engaging == 0) and c.crit_fail == 1):
                # Speed Highest
                if((c.current_speed > c.current_attack) and (c.current_speed > c.current_defense)):
                    c.current_speed -= 2
                # Attack Highest
                elif((c.current_attack > c.current_speed) and (c.current_attack > c.current_defense)):
                    c.current_attack -= 2
                # defense Highest
                elif((c.current_defense > c.current_speed) and (c.current_defense > c.current_attack)):
                    c.current_defense -= 2
                bonus = 0
                if "Sworn Sword T1" in c.perks:
                    bonus += 10
                if "Sworn Sword T2" in c.perks:
                    bonus += 20
                if "Sworn Sword T2" in c.perks:
                    bonus += 30
                critical_fail_injury = secondary_injury_roll(ct, bonus)
                # Critical Injury
                if isinstance(critical_fail_injury, str) and "Critical Injury" in critical_fail_injury:
                    combat_log.append(f"{c.name} suffers {critical_fail_injury} and is taken out!")
                    combat_side_two.pop(c)
                # Major Injury
                if critical_fail_injury == "Major Injury":
                    if "Ageing With Grace" in c.perks:
                        c.current_speed -= 1
                        c.current_attack -= 1
                        c.current_defense -= 1
                    else:
                        c.current_speed -= 2
                        c.current_attack -= 2
                        c.current_defense -= 2
                # Minor Injury
                if critical_fail_injury == "Minor Injury":
                    if "Bloodlust" in c.perks and c.bloodlusted == 0:
                        c.current_speed += 2
                        c.current_attack += 2
                        c.bloodlusted = 1
                    else:
                        c.current_speed -= 1
                        c.current_attack -= 1
                        c.current_defense -= 1
                combat_log.append(f"{c.name} suffers {critical_fail_injury}")
                combat_log.append(f"{c.name} Current Status - Speed: {c.current_speed} | Attack: {c.current_attack} | Defense: {c.current_defense}")

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

        # Check Initiative
        # Iterate Through Combat Side One
        i = 0
        while i < len(combat_side_one):
            c1 = combat_side_one[i]
            c1_init = combat_side_one_initiative[i]
            j = 0
            while j < len(combat_side_two):
                c2 = combat_side_two[j]
                c2_init = combat_side_two_initiative[j]
                # If Combatant Has Rolled Higher
                if ((c1_init > c2_init) and c1.currently_engaging == 0) or (c2.combatants_faced >= c2.max_combatants):
                    combat_log.append(f"{c1.name} attacks {c2.name}!")
                    # Critical Strike
                    if (c1.crit_success == 1):
                        # Speed Highest
                        if((c2.current_speed > c2.current_attack) and (c2.current_speed > c2.current_defense)):
                            c2.current_speed -= 2
                        # Attack Highest
                        elif((c2.current_attack > c2.current_speed) and (c2.current_attack > c2.current_defense)):
                            c2.current_attack -= 2
                        # defense Highest
                        elif((c2.current_defense > c2.current_speed) and (c2.current_defense > c2.current_attack)):
                            c2.current_defense -= 2
                        # Critical Strike Roll - Secondary Injury
                        bonus = 0
                        if "Sworn Sword T1" in c2.perks:
                            bonus += 10
                        if "Sworn Sword T2" in c2.perks:
                            bonus += 20
                        if "Sworn Sword T2" in c2.perks:
                            bonus += 30
                        if (("Valyrian Steel Sword" in c1.items) or ("Qohorik Steel Weapon" in c1.items)) and "Timeless Quality" in c1.perks:
                            bonus -= 20
                        critical_strike_injury = secondary_injury_roll(ct, bonus)
                        # Major / Critical Injury Re-roll - Shield Specialist T3 Perk
                        if (critical_strike_injury == "Major Injury" or critical_strike_injury == "Critical Injury") and "Shield Specialist T3" in c2.perks:
                            critical_strike_injury = secondary_injury_roll(ct, bonus)
                        # Critical Injury Inflicted
                        if isinstance(critical_strike_injury, str) and "Critical Injury" in critical_strike_injury:
                            combat_log.append(f"{c2.name} suffers {critical_strike_injury} and is taken out!")
                            combat_side_two.pop(i)
                            combat_side_two_initiative.pop(i)
                            continue
                        # Major Injury Taken
                        if critical_strike_injury == "Major Injury":
                            c2.major_injuries += 1
                        # Major Injury Check
                        if critical_strike_injury == "Major Injury" and c2.major_injuries > c2.major_injury_buff:
                            if "Ageing With Grace" in c2.perks:
                                c2.current_speed -= 1
                                c2.current_attack -= 1
                                c2.current_defense -= 1
                            else:
                                c2.current_speed -= 2
                                c2.current_attack -= 2
                                c2.current_defense -= 2
                        # Minor Injury
                        if critical_strike_injury == "Minor Injury":
                            if "Bloodlust" in c2.perks and c2.bloodlusted == 0:
                                c2.current_speed += 2
                                c2.current_attack += 2
                                c2.bloodlusted = 1
                            else:
                                c2.current_speed -= 1
                                c2.current_attack -= 1
                                c2.current_defense -= 1
                        combat_log.append(f"{c2.name} suffers {critical_strike_injury}")
                        combat_log.append(f"{c2.name} Current Status - Speed: {c2.current_speed} | Attack: {c2.current_attack} | Defense: {c2.current_defense}")
                    # Status Check
                    c1.currently_engaging = 1
                    c2.combatants_faced += 1
                    # Roll Attack
                    attack_sum, _ = roll_3d5()
                    # Timeless Quality Weapon Checks
                    if ("Timeless Quality" in c1.perks and ("Valyrian Steel Sword" in c1.items or "Qohorik Steel Weapon" in c1.items)) and ("Timeless Quality" in c2.perks and ("Valyrian Steel Armor" in c2.items or "Qohorik Armor" in c2.items)):
                        attack_roll = ((attack_sum + c1.current_attack) - c2.current_defense)
                    elif ("Timeless Quality" in c2.perks and ("Valyrian Steel Armor" in c2.items or "Qohorik Armor" in c2.items)):
                        attack_roll = ((attack_sum + c1.current_attack) - (c2.current_defense*2))
                    elif ("Timeless Quality" in c1.perks and ("Valyrian Steel Sword" in c1.items or "Qohorik Steel Weapon" in c1.items)):
                        attack_roll = ((attack_sum + c1.current_attack) - ((c2.current_defense + 1) // 2))
                    # Normal Attack
                    else:
                        attack_roll = ((attack_sum + c1.current_attack) - c2.current_defense)
                    # Steel Tempest T3 Perk Check
                    if "Steel Tempest T3" in c1.perks:
                        attack_roll = (attack_roll*2)
                    # Minimum Attack - 1
                    if attack_roll <= 0:
                        attack_roll = 1
                    # Deduct Attack From Morale
                    c2.current_morale -= attack_roll
                    combat_log.append(f"{c1.name} attacks {c2.name} → Roll: {attack_sum} + Attack {c1.current_attack} - Defense {c2.current_defense} = {attack_roll}")
                    combat_log.append(f"{c2.name}'s morale drops to {c2.current_morale}")
                    combat_log.append(f"{c2.name} Current Status - Speed: {c2.current_speed} | Attack: {c2.current_attack} | Defense: {c2.current_defense}")
                    # Going Berserk
                    if ((c2.current_morale <= 0) or (c2.current_morale <= c2.morale_threshold)) and "Berserker" in c2.perks and c2.berserked == 0:
                            c2.current_morale += attack_roll
                            c2.current_morale = (c2.current_morale * 2)
                            c2.berserked = 1
                            combat_log.append(f"{c2.name} has gone berserk! Their morale has returned to: {c2.current_morale}")
                    # Combatant Knocked Out
                    if (c2.current_morale <= 0) or (c2.current_morale <= c2.morale_threshold) or (len(c2.injuries) >= c2.injury_threshold):
                        combat_log.append(f"{c2.name} has been defeated!")
                        if(c2.current_morale <= 0):
                            # Roll Primary Injury
                            bonus = 0
                            if "Sworn Sword T1" in c2.perks:
                                bonus += 10
                            if "Sworn Sword T2" in c2.perks:
                                bonus += 20
                            if "Sworn Sword T2" in c2.perks:
                                bonus += 30
                            morale_injury_roll = primary_injury_roll(ct, bonus)
                            combat_log.append(f"{c2.name} has been injured! - {morale_injury_roll}!")
                        combat_side_two.pop()
                        combat_side_two_initiative.pop()
                        continue  # Don't increment j, as list has shifted
                    # Only Take One Attack - Terrifying Presence
                    if ("Terrifying Presence T2" in c2.perks) and (c2.combatants_faced >= 1) and (len(combat_side_two)) == 1:
                        continue
                j += 1
            i += 1
            # Crit Fail & Miss
            if (c1.currently_engaging == 0) and c1.crit_fail == 1:
                # Speed Highest
                if((c1.current_speed > c1.current_attack) and (c1.current_speed > c1.current_defense)):
                    c1.current_speed -= 2
                # Attack Highest
                elif((c1.current_attack > c1.current_speed) and (c1.current_attack > c1.current_defense)):
                    c1.current_attack -= 2
                # Defense Highest
                elif((c1.current_defense > c1.current_speed) and (c1.current_defense > c1.current_attack)):
                    c1.current_defense -= 2
                # Roll Critical Fail - Secondary Injury
                bonus = 0
                if "Sworn Sword T1" in c1.perks:
                    bonus += 10
                if "Sworn Sword T2" in c1.perks:
                    bonus += 20
                if "Sworn Sword T2" in c1.perks:
                    bonus += 30
                critical_fail_injury = secondary_injury_roll(ct, bonus)
                # Shield Specialist T3 Check
                if (critical_fail_injury == "Major Injury" or critical_fail_injury == "Critical Injury") and "Shield Specialist T3" in c1.perks:
                    critical_fail_injury = secondary_injury_roll(ct, bonus)
                # Critical Injury Knockout
                if isinstance(critical_fail_injury, str) and "Critical Injury" in critical_fail_injury:
                    combat_log.append(f"{c1.name} suffers {critical_fail_injury} and is taken out!")
                    combat_side_one.pop(i)
                    combat_side_one_initiative.pop(i)
                # Major Injury Check
                if critical_fail_injury == "Major Injury":
                    c1.major_injuries += 1
                # Major Injury
                if critical_fail_injury == "Major Injury" and c1.major_injuries > c1.major_injury_buff:
                    if "Ageing With Grace" in c1.perks:
                        c1.current_speed -= 1
                        c1.current_attack -= 1
                        c1.current_defense -= 1
                    else:
                        c1.current_speed -= 2
                        c1.current_attack -= 2
                        c1.current_defense -= 2
                # Minor Injury
                if critical_fail_injury == "Minor Injury":
                    if "Bloodlust" in c1.perks and c1.bloodlusted == 0:
                        c1.current_speed += 2
                        c1.current_attack += 2
                        c1.bloodlusted = 1
                    else:
                        c1.current_speed -= 1
                        c1.current_attack -= 1
                        c1.current_defense -= 1
                combat_log.append(f"{c1.name} suffers {critical_fail_injury}")
                combat_log.append(f"{c1.name} Current Status - Speed: {c1.current_speed} | Attack: {c1.current_attack} | Defense: {c1.current_defense}")

        # Iterate Through Combat Side Two
        i = 0
        while i < len(combat_side_two):
            c2 = combat_side_two[i]
            c2_init = combat_side_two_initiative[i]
            j = 0
            while j < len(combat_side_one):
                c1 = combat_side_one[j]
                c1_init = combat_side_one_initiative[j]
                # If Combatant Has Rolled Higher
                if ((combat_side_two_initiative[i] > combat_side_one_initiative[j]) and c2.currently_engaging == 0) or (combat_side_one[j].combatants_faced >= combat_side_one[j].max_combatants):
                    combat_log.append(f"{c2.name} attacks {c1.name}!")
                    # Critical Strike
                    if (combat_side_two[i].crit_success == 1):
                        # Speed Highest
                        if((combat_side_one[j].current_speed > combat_side_one[j].current_attack) and (combat_side_one[j].current_speed > combat_side_one[j].current_defense)):
                            combat_side_one[j].current_speed -= 2
                        # Attack Highest
                        elif((combat_side_one[j].current_attack > combat_side_one[j].current_speed) and (combat_side_one[j].current_attack > combat_side_one[j].current_defense)):
                            combat_side_one[j].current_attack -= 2
                        # Defense Highest
                        elif((combat_side_one[j].current_defense > combat_side_one[j].current_speed) and (combat_side_one[j].current_defense > combat_side_one[j].current_attack)):
                            combat_side_one[j].current_defense -= 2
                        # Critical Strike Roll - Secondary Injury
                        bonus = 0
                        if "Sworn Sword T1" in c1.perks:
                            bonus += 10
                        if "Sworn Sword T2" in c1.perks:
                            bonus += 20
                        if "Sworn Sword T2" in c1.perks:
                            bonus += 30
                        if (("Valyrian Steel Sword" in c2.items) or ("Qohorik Steel Weapon" in c2.items)) and "Timeless Quality" in c2.perks:
                            bonus -= 20
                        critical_strike_injury = secondary_injury_roll(ct, bonus)
                        # Shield Specialist T3 Perk Check
                        if (critical_strike_injury == "Major Injury" or critical_strike_injury == "Critical Injury") and "Shield Specialist T3" in combat_side_one[j].perks:
                            critical_strike_injury = secondary_injury_roll(ct, bonus)
                        # Critical Injury
                        if isinstance(critical_strike_injury, str) and "Critical Injury" in critical_strike_injury:
                            combat_log.append(f"{c1.name} suffers {critical_strike_injury} and is taken out!")
                            combat_side_one.pop(i)
                            combat_side_one_initiative.pop(i)
                        # Major Injury Check
                        if critical_strike_injury == "Major Injury":
                            combat_side_one[j].major_injuries += 1
                        # Major Injury
                        if critical_strike_injury == "Major Injury" and combat_side_one[j].major_injuries > combat_side_one[j].major_injury_buff:
                            if "Ageing With Grace" in c1.perks:
                                c1.current_speed -= 1
                                c1.current_attack -= 1
                                c1.current_defense -= 1
                            else:
                                c1.current_speed -= 2
                                c1.current_attack -= 2
                                c1.current_defense -= 2
                        # Minor Injury
                        if critical_strike_injury == "Minor Injury":
                            if "Bloodlust" in c1.perks and c1.bloodlusted == 0:
                                c1.current_speed += 2
                                c1.current_attack += 2
                                c1.bloodlusted = 1
                            else:
                                c1.current_speed -= 1
                                c1.current_attack -= 1
                                c1.current_defense -= 1
                            combat_log.append(f"{c1.name} suffers {critical_strike_injury}")
                            combat_log.append(f"{c1.name} Current Status - Speed: {c1.current_speed} | Attack: {c1.current_attack} | Defense: {c1.current_defense}")
                    # Status Check
                    c2.currently_engaging = 1
                    c1.combatants_faced += 1
                    # Roll Attack
                    attack_sum, _ = roll_3d5()
                    # Timeless Quality Perk Check
                    if ("Timeless Quality" in c2.perks and ("Valyrian Steel Sword" in c2.items or "Qohorik Steel Weapon" in c2.items)) and ("Timeless Quality" in c1.perks and ("Valyrian Steel Armor" in c1.items or "Qohorik Armor" in c1.items)):
                        attack_roll = ((attack_sum + c2.current_attack) - c1.current_defense)
                    elif ("Timeless Quality" in c1.perks and ("Valyrian Steel Armor" in c1.items or "Qohorik Armor" in c1.items)):
                        attack_roll = ((attack_sum + c2.current_attack) - (c1.current_defense*2))
                    elif ("Timeless Quality" in c2.perks and ("Valyrian Steel Sword" in c2.items or "Qohorik Steel Weapon" in c2.items)):
                        attack_roll = ((attack_sum + c2.current_attack) - ((c1.current_defense + 1) // 2))
                    # Normal Attack Roll
                    else:
                        attack_roll = ((attack_sum + c2.current_attack) - c1.current_defense)
                    # Steel Tempest T3 - Double Attack
                    if "Steel Tempest T3" in c1.perks:
                        attack_roll = (attack_roll*2)
                    # Minimum Attack = 1
                    if attack_roll <= 0:
                        attack_roll = 1
                    # Deduct Attack From Morale
                    c1.current_morale -= attack_roll
                    combat_log.append(f"{c2.name} attacks {c1.name} → Roll: {attack_sum} + Attack {c2.current_attack} - Defense {c1.current_defense} = {attack_roll}")
                    combat_log.append(f"{c1.name}'s morale drops to {c1.current_morale}")
                    combat_log.append(f"{c1.name} Current Status - Speed: {c1.current_speed} | Attack: {c1.current_attack} | Defense: {c1.current_defense}")
                    # Going Berserk
                    if ((c1.current_morale <= 0) or (c1.current_morale <= c1.morale_threshold)) and "Berserker" in c1.perks and c1.berserked == 0:
                            c1.current_morale += attack_roll
                            c1.current_morale = (c1.current_morale * 2)
                            c1.berserked = 1
                            combat_log.append(f"{c1.name} has gone berserk! Their morale has returned to: {c1.current_morale}")
                    # Combatant Knocked Out
                    if (c1.current_morale <= 0) or (c1.current_morale <= c1.morale_threshold) or (len(c1.injuries) >= c1.injury_threshold):
                        combat_log.append(f"{c1.name} has been defeated!")
                        if(c1.current_morale <= 0):
                            # Roll Primary Injury
                            bonus = 0
                            if "Sworn Sword T1" in c1.perks:
                                bonus += 10
                            if "Sworn Sword T2" in c1.perks:
                                bonus += 20
                            if "Sworn Sword T2" in c1.perks:
                                bonus += 30
                            morale_injury_roll = primary_injury_roll(ct, bonus)
                            combat_log.append(f"{c1.name} has been injured! - {morale_injury_roll}!")
                        combat_side_one.pop(j)
                        combat_side_one_initiative.pop(j)
                        continue  # Don't increment j, as list has shifted
                    # Take Only One Attack - Terrifying Presence T2 Perk Check
                    if ("Terrifying Presence T2" in c1.perks) and (c1.combatants_faced >= 1) and (len(combat_side_one)) == 1:
                        continue
                j += 1
            
            # Crit Fail & Miss
            if (c2.currently_engaging == 0) and c2.crit_fail == 1:
                # Speed Highest
                if((c2.current_speed > c2.current_attack) and (c2.current_speed > c2.current_defense)):
                    c2.current_speed -= 2
                # Attack Highest
                elif((c2.current_attack > c2.current_speed) and (c2.current_attack > c2.current_defense)):
                    c2.current_attack -= 2
                # defense Highest
                elif((c2.current_defense > c2.current_speed) and (c2.current_defense > c2.current_attack)):
                    c2.current_defense -= 2
                # Critical Fail Roll - Secondary Injury
                bonus = 0
                if "Sworn Sword T1" in c2.perks:
                    bonus += 10
                if "Sworn Sword T2" in c2.perks:
                    bonus += 20
                if "Sworn Sword T2" in c2.perks:
                    bonus += 30
                critical_fail_injury = secondary_injury_roll(ct, bonus)
                # Shield Specialist T3 - Perk Check
                if (critical_fail_injury == "Major Injury" or critical_fail_injury == "Critical Injury") and "Shield Specialist T3" in c2.perks:
                    critical_fail_injury = secondary_injury_roll(ct, bonus)
                # Critical Injury
                if isinstance(critical_fail_injury, str) and "Critical Injury" in critical_fail_injury:
                    combat_log.append(f"{c2.name} suffers {critical_fail_injury} and is taken out!")
                    combat_side_two.pop(i)
                    combat_side_two_initiative.pop(i)
                # Major Injury
                if critical_fail_injury == "Major Injury":
                    if "Ageing With Grace" in c2.perks:
                        c2.current_speed -= 1
                        c2.current_attack -= 1
                        c2.current_defense -= 1
                    else:
                        c2.current_speed -= 2
                        c2.current_attack -= 2
                        c2.current_defense -= 2
                # Minor Injury
                if critical_fail_injury == "Minor Injury":
                    if "Bloodlust" in c2.perks and c2.bloodlusted == 0:
                        c2.current_speed += 2
                        c2.current_attack += 2
                        c2.bloodlusted = 1
                    else:
                        c2.current_speed -= 1
                        c2.current_attack -= 1
                        c2.current_defense -= 1
                combat_log.append(f"{c2.name} suffers {critical_fail_injury}")
                combat_log.append(f"{c2.name} Current Status - Speed: {c2.current_speed} | Attack: {c2.current_attack} | Defense: {c2.current_defense}")
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
            combat_log.append("This round has ended in a stalemate, neither side have made progress.")

        # End Of Round
        # Print Round
        combat_log.append("==============================================================")
        combat_log_string(combat_log)
        combat_log = []
        # Reset Initiative
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
        combat_log.append("Side Two has won this duel!")
        combat_log_string(combat_log)
        combat_log = []

    if len(combat_side_two) == 0:
        combat_log.append("Side One has won this duel!")
        combat_log_string(combat_log)
        combat_log = []

######################################################################################################
# Combat Scenario - Ranged vs Melee
######################################################################################################

def ranged_melee(side1, side2, ct):

    # Combat Log
    combat_log = []
    round_count = 0  

    # Side Initialization
    combat_side_one = side_initialization(side1)
    combat_side_two = side_initialization(side2)
    # Stat Initialization
    for i in range(len(combat_side_one)):
        ranged_initialization(combat_side_one[i])
    for j in range(len(combat_side_two)):
        melee_initialization(combat_side_two[j])

    # Log fighters and their teams before combat starts
    combat_log.append("==============================================================")
    if not combat_log:
        combat_log.append("Side 1")
        for c in combat_side_one:
            combat_log.append(
                f"  {c.name} - Speed: {c.current_speed} | Attack: {c.current_attack} | Defense: {c.current_defense} | Morale: {c.current_morale} | Perks: {c.perks} | Injury Malus: {c.injuries} | Items: {c.items}"
            )
        combat_log.append("Side 2")
        for c in combat_side_two:
            combat_log.append(
                f"  {c.name} - Speed: {c.current_speed} | Attack: {c.current_attack} | Defense: {c.current_defense} | Morale: {c.current_morale} | Perks: {c.perks} | Injury Malus: {c.injuries} | Items: {c.items}"
            )
    combat_log.append("==============================================================")

    # Battlefield Champion T3 Check
    # Side One
    bc3_count = 0
    bc3_check = 0
    for c in combat_side_one:
        if "Battlefield Champion T3" in c.perks:
            for d in combat_side_one:
                if(bc3_count != bc3_check):
                    d.current_morale += 7
                bc3_check +=1
            combat_log.append(f"The presence of the Battlefield Champion {c.name} boosts the morale of the men around them!")
        bc3_count += 1
        
    # Side Two
    bc3_count = 0
    bc3_check = 0
    for e in combat_side_two:
        if "Battlefield Champion T3" in e.perks:
            for f in combat_side_one:
                if(bc3_count != bc3_check):
                    f.current_morale += 7
                bc3_check +=1
            combat_log.append(f"The presence of the Battlefield Champion {e.name} boosts the morale of the men around them!")
        bc3_count += 1
    
    # Stage One - Ranged Attacks
    # Keep Track
    ranged_rounds = 0
    while len(combat_side_one) > 0 and len(combat_side_two) > 0:

        round_count += 1
        combat_log.append("==============================================================")

        if (len(combat_side_one) == 1) and len(combat_side_two) > 1 and ("Terrifying Presence T1" in combat_side_one[0].perks) and (combat_side_one[0].imposed_presence == 0):
            combat_side_one[0].imposed_presence = 1
            for c in combat_side_two:
                c.morale_threshold += 10
            combat_log.append(f"The terrifying presence of {combat_side_one[0].name} strikes fear into the heart of their enemies!")
        if (len(combat_side_two) == 1) and len(combat_side_one) > 1 and ("Terrifying Presence T1" in combat_side_two[0].perks) and (combat_side_two[0].imposed_presence == 0):
            combat_side_two[0].imposed_presence = 1
            for c in combat_side_one:
                c.morale_threshold += 10
            combat_log.append(f"The terrifying presence of {combat_side_two[0].name} strikes fear into the heart of their enemies!")
        if (len(combat_side_one) == 1) and len(combat_side_two) > 1 and ("Terrifying Presence T2" in combat_side_one[0].perks) and (combat_side_one[0].imposed_presence == 0):
            combat_side_one[0].imposed_presence = 1
            for c in combat_side_two:
                c.morale_threshold += 15
            combat_log.append(f"The terrifying presence of {combat_side_one[0].name} strikes fear into the heart of their enemies!")
        if (len(combat_side_two) == 1) and len(combat_side_one) > 1 and ("Terrifying Presence T2" in combat_side_two[0].perks) and (combat_side_two[0].imposed_presence == 0):
            combat_side_two[0].imposed_presence = 1
            for c in combat_side_one:
                c.morale_threshold += 15
            combat_log.append(f"The terrifying presence of {combat_side_two[0].name} strikes fear into the heart of their enemies!")

        combat_side_one_initiative = []
        for c in combat_side_one:
            initiative_sum, _ = roll_2d20()
            combat_log.append(f"{c.name} rolls initiative: {_} + Speed {c.current_speed} = {initiative_sum + c.current_speed}")
            if ("Born Lucky" in c.perks) and (1 in _) and c.you_lucky == 0:
                c.you_lucky = 1
                initiative_sum, _ = roll_2d20()
                combat_log.append(f"{c.name} is lucky! They re-roll their initiative: {initiative_sum} + Speed {c.current_speed} = {initiative_sum + c.current_speed}")
            combat_side_one_initiative.append(initiative_sum + c.current_speed)
            if 1 in _:
                c.crit_fail = 1
                combat_log.append(f"{c.name} rolls a Critical Fail!")
            if 20 in _:
                c.crit_success = 1
                combat_log.append(f"{c.name} rolls a Critical Success!")
            if 1 in _ and 20 in _:
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
                    combat_log.append(f"{c1.name} attacks {c2.name}!")
                    # Critical Strike
                    if (combat_side_one[i].crit_success == 1):
                        if((combat_side_two[j].current_speed > combat_side_two[j].current_attack) and (combat_side_two[j].current_speed > combat_side_two[j].current_defense)):
                            combat_side_two[j].current_speed -= 2
                        elif((combat_side_two[j].current_attack > combat_side_two[j].current_speed) and (combat_side_two[j].current_attack > combat_side_two[j].current_defense)):
                            combat_side_two[j].current_attack -= 2
                        elif((combat_side_two[j].current_defense > combat_side_two[j].current_speed) and (combat_side_two[j].current_defense > combat_side_two[j].current_attack)):
                            combat_side_two[j].current_defense -= 2
                        bonus = 0
                        if "Sworn Sword T1" in c2.perks:
                            bonus += 10
                        if "Sworn Sword T2" in c2.perks:
                            bonus += 20
                        if "Sworn Sword T2" in c2.perks:
                            bonus += 30
                        critical_strike_injury = secondary_injury_roll(ct, bonus)
                        if isinstance(critical_strike_injury, str) and "Critical Injury" in critical_strike_injury:
                            combat_log.append(f"{c2.name} suffers {critical_strike_injury} and is taken out!")
                            combat_side_two.pop(i)
                        if critical_strike_injury == "Major Injury":
                            if "Ageing With Grace" in c2.perks:
                                c2.current_speed -= 1
                                c2.current_attack -= 1
                                c2.current_defense -= 1
                            else:
                                c2.current_speed -= 2
                                c2.current_attack -= 2
                                c2.current_defense -= 2
                        if critical_strike_injury == "Minor Injury":
                            if "Bloodlust" in c2.perks and c2.bloodlusted == 0:
                                c2.current_speed += 2
                                c2.current_attack += 2
                                c2.bloodlusted = 1
                            else:
                                c2.current_speed -= 1
                                c2.current_attack -= 1
                                c2.current_defense -= 1
                        combat_log.append(f"{c2.name} suffers {critical_strike_injury}")
                        combat_log.append(f"{c2.name} Current Status - Speed: {c2.current_speed} | Attack: {c2.current_attack} | Defense: {c2.current_defense}")
                    c1.currently_engaging = 1
                    c2.combatants_faced += 1
                    attack_sum, _ = roll_3d5()
                    attack_roll = ((attack_sum + c1.current_attack) - c2.current_defense)
                    if attack_roll <= 0:
                        attack_roll = 1
                    c2.current_morale -= attack_roll
                    combat_log.append(f"{c1.name} attacks {c2.name} → Roll: {attack_sum} + Attack {c1.current_attack} - Defense {c2.current_defense} = {attack_roll}")
                    combat_log.append(f"{c2.name}'s morale drops to {c2.current_morale}")
                    combat_log.append(f"{c2.name} Current Status - Speed: {c2.current_speed} | Attack: {c2.current_attack} | Defense: {c2.current_defense}")
                    if ((c2.current_morale <= 0) or (c2.current_morale <= c2.morale_threshold)) and "Berserker" in c2.perks and c2.berserked == 0:
                        c2.current_morale += attack_roll
                        c2.current_morale = (c2.current_morale * 2)
                        c2.berserked = 1
                        combat_log.append(f"{c2.name} has gone berserk! Their morale has returned to: {c2.current_morale}")
                    if (c2.current_morale <= 0) or (c2.current_morale <= c2.morale_threshold) or (len(c2.injuries) >= c2.injury_threshold):
                        combat_log.append(f"{c2.name} has been defeated!")
                        if(c2.current_morale <= 0):
                            # Roll Primary Injury
                            bonus = 0
                            if "Sworn Sword T1" in c2.perks:
                                bonus += 10
                            if "Sworn Sword T2" in c2.perks:
                                bonus += 20
                            if "Sworn Sword T2" in c2.perks:
                                bonus += 30
                            morale_injury_roll = primary_injury_roll(ct, bonus)
                            combat_log.append(f"{c2.name} has been injured! - {morale_injury_roll}!")
                        combat_side_two.pop(j)
                        continue  # Don't increment j, as list has shifted
                    if ("Terrifying Presence T2" in c2.perks) and (c2.combatants_faced >= 1) and (len(combat_side_two)) == 1:
                        continue
                j += 1
            i += 1
            if ((c1.currently_engaging == 0) and c1.crit_fail == 1) and (c1.max_mixed_rounds >= ranged_rounds):
                if((c1.current_speed > c1.current_attack) and (c1.current_speed > c1.current_defense)):
                    c1.current_speed -= 2
                elif((c1.current_attack > c1.current_speed) and (c1.current_attack > c1.current_defense)):
                    c1.current_attack -= 2
                elif((c1.current_defense > c1.current_speed) and (c1.current_defense > c1.current_attack)):
                    combat_side_two[i].current_defense -= 2
                bonus = 0
                if "Sworn Sword T1" in c1.perks:
                    bonus += 10
                if "Sworn Sword T2" in c1.perks:
                    bonus += 20
                if "Sworn Sword T2" in c1.perks:
                    bonus += 30
                critical_fail_injury = secondary_injury_roll(ct, bonus)
                if isinstance(critical_fail_injury, str) and "Critical Injury" in critical_fail_injury:
                    combat_log.append(f"{c1.name} suffers {critical_fail_injury} and is taken out!")
                    combat_side_one.pop(i)
                    combat_side_one_initiative.pop(i)
                if critical_fail_injury == "Major Injury":
                    if "Ageing With Grace" in c1.perks:
                        c1.current_speed -= 1
                        c1.current_attack -= 1
                        c1.current_defense -= 1
                    else:
                        c1.current_speed -= 2
                        c1.current_attack -= 2
                        c1.current_defense -= 2
                if critical_fail_injury == "Minor Injury":
                    if "Bloodlust" in c1.perks and c1.bloodlusted == 0:
                        c1.current_speed += 2
                        c1.current_attack += 2
                        c1.bloodlusted = 1
                    else:
                        c1.current_speed -= 1
                        c1.current_attack -= 1
                        c1.current_defense -= 1
                combat_log.append(f"{c1.name} suffers {critical_fail_injury}")
                combat_log.append(f"{c1.name} Current Status - Speed: {c1.current_speed} | Attack: {c1.current_attack} | Defense: {c1.current_defense}")
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
            combat_log.append("This round has ended in a stalemate, neither side have made progress.")

        # End Of Round
        # Print Round
        combat_log.append("==============================================================")
        combat_log_string(combat_log)
        combat_log = []
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

        if len(combat_side_one) == 0:
            combat_log.append("Side Two has won this duel!")
            combat_log_string(combat_log)
            combat_log = []
            continue

        if len(combat_side_two) == 0:
            combat_log.append("Side One has won this duel!")
            combat_log_string(combat_log)
            combat_log = []
            continue

        # Are We Done?
        continue_duel = 0
        for c in combat_side_one:
            if c.max_mixed_rounds >= ranged_rounds:
                continue_duel += 1
        
        if continue_duel == 0:
            break

    # Stage 1.5 - Thrown Projectiles
    for c in combat_side_two:
        if "Thrown Projectile Specialist T2" in c.perks:

            round_count += 1

            initiative_sum, _ = roll_2d20()
            combat_log.append(f"{c.name} rolls initiative: {_} + Speed {c.current_speed} = {initiative_sum + c.current_speed}")
            if ("Born Lucky" in c.perks) and (1 in _) and c.you_lucky == 0:
                c.you_lucky = 1
                initiative_sum, _ = roll_2d20()
                combat_log.append(f"{c.name} is lucky! They re-roll their initiative: {initiative_sum} + Speed {c.current_speed} = {initiative_sum + c.current_speed}")
            if 1 in _:
                c.crit_fail = 1
                combat_log.append(f"{c.name} rolls a Critical Fail!")
            if 20 in _:
                c.crit_success = 1
                combat_log.append(f"{c.name} rolls a Critical Success!")
            if 1 in _ and 20 in _:
                c.crit_fail = 0
                c.crit_success = 0
            
            target = random.sample(combat_side_one, 1)[0]
            target_index = combat_side_one.index(target)

            if ((initiative_sum >= 30) or (target.combatants_faced >= target.max_combatants)):
                combat_log.append(f"{c.name} attacks {target.name}!")
                # Critical Strike
                if (c.crit_success == 1):
                    if((target.current_speed > target.current_attack) and (target.current_speed > target.current_defense)):
                        target.current_speed -= 2
                    elif((target.current_attack > target.current_speed) and (target.current_attack > target.current_defense)):
                        target.current_attack -= 2
                    elif((target.current_defense > target.current_speed) and (target.current_defense > target.current_attack)):
                        target.current_defense -= 2
                    bonus = 0
                    if "Sworn Sword T1" in target.perks:
                        bonus += 10
                    if "Sworn Sword T2" in target.perks:
                        bonus += 20
                    if "Sworn Sword T2" in target.perks:
                        bonus += 30
                    critical_strike_injury = secondary_injury_roll(ct, bonus)
                    if isinstance(critical_strike_injury, str) and "Critical Injury" in critical_strike_injury:
                        combat_log.append(f"{target.name} suffers {critical_strike_injury} and is taken out!")
                        combat_side_one.pop(target_index)
                    if critical_strike_injury == "Major Injury":
                        if "Ageing With Grace" in c.perks:
                            target.current_speed -= 1
                            target.current_attack -= 1
                            target.current_defense -= 1
                        else:
                            target.current_speed -= 2
                            target.current_attack -= 2
                            target.current_defense -= 2
                    if critical_strike_injury == "Minor Injury":
                        if "Bloodlust" in target.perks and target.bloodlusted == 0:
                            target.current_speed += 2
                            target.current_attack += 2
                            target.bloodlusted = 1
                        else:
                            target.current_speed -= 1
                            target.current_attack -= 1
                            target.current_defense -= 1
                    combat_log.append(f"{target.name} suffers {critical_strike_injury}")
                    combat_log.append(f"{target.name} Current Status - Speed: {target.current_speed} | Attack: {target.current_attack} | Defense: {target.current_defense}")
                c.currently_engaging = 1
                target.combatants_faced += 1
                attack_sum, _ = roll_3d5()
                attack_roll = ((attack_sum + c.current_attack) - target.current_defense)
                if attack_roll <= 0:
                    attack_roll = 1
                target.current_morale -= attack_roll
                combat_log.append(f"{c.name} attacks {target.name} → Roll: {attack_sum} + Attack {c.current_attack} - Defense {target.current_defense} = {attack_roll}")
                combat_log.append(f"{target.name}'s morale drops to {target.current_morale}")
                combat_log.append(f"{target.name} Current Status - Speed: {target.current_speed} | Attack: {target.current_attack} | Defense: {target.current_defense}")
                if ((target.current_morale <= 0) or (target.current_morale <= target.morale_threshold)) and "Berserker" in target.perks and target.berserked == 0:
                    target.current_morale += attack_roll
                    target.current_morale = (target.current_morale * 2)
                    target.berserked = 1
                    combat_log.append(f"{target.name} has gone berserk! Their morale has returned to: {target.current_morale}")
                if (target.current_morale <= 0) or (target.current_morale <= target.morale_threshold) or (len(target.injuries) >= target.injury_threshold):
                    combat_log.append(f"{target.name} has been defeated!")
                    if(target.current_morale <= 0):
                        # Roll Primary Injury
                        bonus = 0
                        if "Sworn Sword T1" in target.perks:
                            bonus += 10
                        if "Sworn Sword T2" in target.perks:
                            bonus += 20
                        if "Sworn Sword T2" in target.perks:
                            bonus += 30
                        morale_injury_roll = primary_injury_roll(ct, bonus)
                        combat_log.append(f"{target.name} has been injured! - {morale_injury_roll}!")
                    combat_side_one.pop(target_index)
                if ("Terrifying Presence T2" in target.perks) and (target.combatants_faced >= 1) and (len(combat_side_one)) == 1:
                    continue
            if ((c.currently_engaging == 0) and c.crit_fail == 1) and (c.max_mixed_rounds >= ranged_rounds):
                if((c.current_speed > c.current_attack) and (c.current_speed > c.current_defense)):
                    c.current_speed -= 2
                elif((c.current_attack > c.current_speed) and (c.current_attack > c.current_defense)):
                    c.current_attack -= 2
                elif((c.current_defense > c.current_speed) and (c.current_defense > c.current_attack)):
                    c.current_defense -= 2
                bonus = 0
                if "Sworn Sword T1" in c.perks:
                    bonus += 10
                if "Sworn Sword T2" in c.perks:
                    bonus += 20
                if "Sworn Sword T2" in c.perks:
                    bonus += 30
                critical_fail_injury = secondary_injury_roll(ct, bonus)
                if isinstance(critical_fail_injury, str) and "Critical Injury" in critical_fail_injury:
                    combat_log.append(f"{c.name} suffers {critical_fail_injury} and is taken out!")
                    combat_side_one.pop(c)
                if critical_fail_injury == "Major Injury":
                    if "Ageing With Grace" in c.perks:
                        c.current_speed -= 1
                        c.current_attack -= 1
                        c.current_defense -= 1
                    else:
                        c.current_speed -= 2
                        c.current_attack -= 2
                        c.current_defense -= 2
                if critical_fail_injury == "Minor Injury":
                    if "Bloodlust" in c.perks and c.bloodlusted == 0:
                        c.current_speed += 2
                        c.current_attack += 2
                        c.bloodlusted = 1
                    else:
                        c.current_speed -= 1
                        c.current_attack -= 1
                        c.current_defense -= 1
                combat_log.append(f"{c.name} suffers {critical_fail_injury}")
                combat_log.append(f"{c.name} Current Status - Speed: {c.current_speed} | Attack: {c.current_attack} | Defense: {c.current_defense}")

            # Print Round
            round_count += 1
            combat_log.append("==============================================================")
            combat_log_string(combat_log)
            combat_log = []

            if len(combat_side_one) == 0:
                combat_log.append("Side Two has won this duel!")
                combat_log_string(combat_log)
                combat_log = []
                continue

            if len(combat_side_two) == 0:
                combat_log.append("Side One has won this duel!")
                combat_log_string(combat_log)
                combat_log = []
                continue

    # Stage 2
    while len(combat_side_one) > 0 and len(combat_side_two) > 0:

        round_count += 1

        # Iterate Through Combat Side Two
        i = 0
        while i < len(combat_side_two):
            c2 = combat_side_two[i]
            j = 0
            while j < len(combat_side_one):
                c1 = combat_side_one[j]
                combat_log.append(f"{c2.name} attacks {c1.name}!")
                # One Combatant Only
                c2.currently_engaging = 1
                c1.combatants_faced += 1
                # Roll Attack
                attack_sum, _ = roll_3d5()
                attack_roll = ((attack_sum + c2.current_attack) - c1.current_defense)
                if attack_roll <= 0:
                    attack_roll = 1
                c1.current_morale -= attack_roll
                combat_log.append(f"{c2.name} attacks {c1.name} → Roll: {attack_sum} + Attack {c2.current_attack} - Defense {c1.current_defense} = {attack_roll}")
                combat_log.append(f"{c1.name}'s morale drops to {c1.current_morale}")
                combat_log.append(f"{c1.name} Current Status - Speed: {c1.current_speed} | Attack: {c1.current_attack} | Defense: {c1.current_defense}")
                if ((c1.current_morale <= 0) or (c1.current_morale <= c1.morale_threshold)) and "Berserker" in c1.perks and c1.berserked == 0:
                        c1.current_morale += attack_roll
                        c1.current_morale = (c1.current_morale * 2)
                        c1.berserked = 1
                        combat_log.append(f"{c1.name} has gone berserk! Their morale has returned to: {c1.current_morale}")
                if (c1.current_morale <= 0) or (c1.current_morale <= c1.morale_threshold) or (len(c1.injuries) >= c1.injury_threshold):
                    combat_log.append(f"{c1.name} has been defeated!")
                    if(c1.current_morale <= 0):
                        # Roll Primary Injury
                        bonus = 0
                        if "Sworn Sword T1" in c1.perks:
                            bonus += 10
                        if "Sworn Sword T2" in c1.perks:
                            bonus += 20
                        if "Sworn Sword T2" in c1.perks:
                            bonus += 30
                        morale_injury_roll = primary_injury_roll(ct, bonus)
                        combat_log.append(f"{c1.name} has been injured! - {morale_injury_roll}!")
                    combat_side_one.pop(j)
                    continue  # Don't increment j, as list has shifted
                if ("Terrifying Presence T2" in c1.perks) and (c1.combatants_faced >= 1) and (len(combat_side_one)) == 1:
                    continue
                j += 1
            i += 1

        # End Of Round
        # Print Round
        combat_log.append("==============================================================")
        combat_log_string(combat_log)
        combat_log = []
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
            combat_log.append("Side Two has won this duel!")
            combat_log_string(combat_log)
            combat_log = []
            continue

        if len(combat_side_two) == 0:
            combat_log.append("Side One has won this duel!")
            combat_log_string(combat_log)
            combat_log = []
            continue

        break

    # Switch Context Initialization
    for i in range(len(combat_side_one)):
        mixed_initialization(combat_side_one[i])

    # Stage 3
    # While Both Teams Have Combatants
    # While Both Teams Have Combatants
    while len(combat_side_one) > 0 and len(combat_side_two) > 0:

        round_count += 1
        combat_log.append("==============================================================")

        # Terrifying Presence T1 Check
        # Side One
        if (len(combat_side_one) == 1) and len(combat_side_two) > 1 and ("Terrifying Presence T1" in combat_side_one[0].perks) and (combat_side_one[0].imposed_presence == 0):
            combat_side_one[0].imposed_presence = 1
            for c in combat_side_two:
                c.morale_threshold += 10
            combat_log.append(f"The terrifying presence of {combat_side_one[0].name} strikes fear into the heart of their enemies!")
        # Side Two
        if (len(combat_side_two) == 1) and len(combat_side_one) > 1 and ("Terrifying Presence T1" in combat_side_two[0].perks) and (combat_side_two[0].imposed_presence == 0):
            combat_side_two[0].imposed_presence = 1
            for c in combat_side_one:
                c.morale_threshold += 10
            combat_log.append(f"The terrifying presence of {combat_side_two[0].name} strikes fear into the heart of their enemies!")
        # Terrifying Presence T2 Check
        # Side One
        if (len(combat_side_one) == 1) and len(combat_side_two) > 1 and ("Terrifying Presence T2" in combat_side_one[0].perks) and (combat_side_one[0].imposed_presence == 0):
            combat_side_one[0].imposed_presence = 1
            for c in combat_side_two:
                c.morale_threshold += 15
            combat_log.append(f"The terrifying presence of {combat_side_one[0].name} strikes fear into the heart of their enemies!")
        # Side Two
        if (len(combat_side_two) == 1) and len(combat_side_one) > 1 and ("Terrifying Presence T2" in combat_side_two[0].perks) and (combat_side_two[0].imposed_presence == 0):
            combat_side_two[0].imposed_presence = 1
            for c in combat_side_one:
                c.morale_threshold += 15
            combat_log.append(f"The terrifying presence of {combat_side_two[0].name} strikes fear into the heart of their enemies!")
        # Roll Initiative
        # Side One
        combat_side_one_initiative = []
        for c in combat_side_one:
            initiative_sum, _ = roll_2d20()
            combat_log.append(f"{c.name} rolls initiative: {_} + Speed {c.current_speed} = {initiative_sum + c.current_speed}")
            # Born Lucky Perk Check
            if ("Born Lucky" in c.perks) and (1 in _) and c.you_lucky == 0:
                c.you_lucky = 1
                initiative_sum, _ = roll_2d20()
                combat_log.append(f"{c.name} is lucky! They re-roll their initiative: {initiative_sum} + Speed {c.current_speed} = {initiative_sum + c.current_speed}")
            combat_side_one_initiative.append(initiative_sum + c.current_speed)
            # Combat Log
            # Crit Checks
            if 1 in _:
                c.crit_fail = 1
                combat_log.append(f"{c.name} rolls a Critical Fail!")
            if 20 in _:
                c.crit_success = 1
                combat_log.append(f"{c.name} rolls a Critical Success!")
            if 19 in _ and "Duelist T3" in c.perks:
                c.crit_success = 1
                combat_log.append(f"{c.name} rolls a Critical Success!")
            if 1 in _ and 20 in _:
                c.crit_fail = 0
                c.crit_success = 0
            # Thrown Projectile Specialist T3 - Free Throw
            if initiative_sum >= 30 and "Thrown Projectile Specialist T3" in c.perks and round_count == 1:
                # Random Target Chosen
                target = random.sample(combat_side_two, 1)[0]
                target_index = combat_side_two.index(target)
                combat_log.append(f"{c.name} throws a projectile at {target.name}")
                # Critical Strike
                if (c.crit_success == 1):
                    # Speed Highest
                    if((target.current_speed > target.current_attack) and (target.current_speed > target.current_defense)):
                        target.current_speed -= 2
                    # Attack Highest
                    elif((target.current_attack > target.current_speed) and (target.current_attack > target.current_defense)):
                        target.current_attack -= 2
                    # defense Highest
                    elif((target.current_defense > target.current_speed) and (target.current_defense > target.current_attack)):
                        target.current_defense -= 2
                    bonus = 0
                    if "Sworn Sword T1" in target.perks:
                        bonus += 10
                    if "Sworn Sword T2" in target.perks:
                        bonus += 20
                    if "Sworn Sword T2" in target.perks:
                        bonus += 30
                    critical_strike_injury = secondary_injury_roll(ct, bonus)
                    # Critical Injury
                    if isinstance(critical_strike_injury, str) and "Critical Injury" in critical_strike_injury:
                        combat_log.append(f"{target.name} suffers {critical_strike_injury} and is taken out!")
                        combat_side_two.pop(target_index)
                        continue
                    # Major Injury
                    if critical_strike_injury == "Major Injury":
                        if "Ageing With Grace" in target.perks:
                            target.current_speed -= 1
                            target.current_attack -= 1
                            target.current_defense -= 1
                        else:
                            target.current_speed -= 2
                            target.current_attack -= 2
                            target.current_defense -= 2
                    # Minor Injury
                    if critical_strike_injury == "Minor Injury":
                        if "Bloodlust" in target.perks and target.bloodlusted == 0:
                            target.current_speed += 2
                            target.current_attack += 2
                            target.bloodlusted = 1
                        else:
                            target.current_speed -= 1
                            target.current_attack -= 1
                            target.current_defense -= 1
                    combat_log.append(f"{target.name} suffers {critical_strike_injury}")
                    combat_log.append(f"{target.name} Current Status - Speed: {target.current_speed} | Attack: {target.current_attack} | Defense: {target.current_defense}")
                # Status Checks
                c.currently_engaging = 1
                target.combatants_faced += 1
                # Attack Roll
                attack_sum, _ = roll_3d5()
                attack_roll = ((attack_sum + c.current_attack) - target.current_defense)
                # Steel Tempest Perk Check
                if "Steel Tempest T3" in c.perks:
                    attack_roll = (attack_roll*2)
                # Minimum Attack - 1
                if attack_roll <= 0:
                    attack_roll = 1
                # Deduct From Morale
                target.current_morale -= attack_roll
                combat_log.append(f"{c.name} attacks {target.name} → Roll: {attack_sum} + Attack {c.current_attack} - Defense {target.current_defense} = {attack_roll}")
                combat_log.append(f"{target.name}'s morale drops to {target.current_morale}")
                combat_log.append(f"{target.name} Current Status - Speed: {target.current_speed} | Attack: {target.current_attack} | Defense: {target.current_defense}")
                # Activate Berserker Rage Perk
                if ((target.current_morale <= 0) or (target.current_morale <= target.morale_threshold)) and "Berserker" in target.perks and target.berserked == 0:
                    target.current_morale += attack_roll
                    target.current_morale = (target.current_morale * 2)
                    target.berserked = 1
                    combat_log.append(f"{target.name} has gone berserk! Their morale has returned to: {target.current_morale}")
                # Duel End
                if (target.current_morale <= 0) or (target.current_morale <= target.morale_threshold) or (len(target.injuries) >= target.injury_threshold):
                    # If Below Morale
                    combat_log.append(f"{target.name} has been defeated!")
                    if(target.current_morale <= 0):
                        # Roll Primary Injury
                        bonus = 0
                        if "Sworn Sword T1" in target.perks:
                            bonus += 10
                        if "Sworn Sword T2" in target.perks:
                            bonus += 20
                        if "Sworn Sword T2" in target.perks:
                            bonus += 30
                        morale_injury_roll = primary_injury_roll(ct, bonus)
                        combat_log.append(f"{target.name} has been injured! - {morale_injury_roll}!")
                    combat_side_two.pop(target_index)
                # If Terrifying Presence - Only Take One Hit
                if ("Terrifying Presence T2" in target.perks) and (target.combatants_faced >= 1) and (len(combat_side_two)) == 1:
                    continue
            # Crit Fail & Missed Opponents
            if ((c.currently_engaging == 0) and c.crit_fail == 1) and initiative_sum < 30 and "Thrown Projectile Specialist T3" in c.perks and round_count == 1:
                # Speed Highest
                if((c.current_speed > c.current_attack) and (c.current_speed > c.current_defense)):
                    c.current_speed -= 2
                # Attack Highest
                elif((c.current_attack > c.current_speed) and (c.current_attack > c.current_defense)):
                    c.current_attack -= 2
                # defense Highest
                elif((c.current_defense > c.current_speed) and (c.current_defense > c.current_attack)):
                    c.current_defense -= 2
                bonus = 0
                if "Sworn Sword T1" in c.perks:
                    bonus += 10
                if "Sworn Sword T2" in c.perks:
                    bonus += 20
                if "Sworn Sword T2" in c.perks:
                    bonus += 30
                critical_fail_injury = secondary_injury_roll(ct, bonus)
                # Critical Injury
                if isinstance(critical_fail_injury, str) and "Critical Injury" in critical_fail_injury:
                    combat_log.append(f"{c.name} suffers {critical_fail_injury} and is taken out!")
                    combat_side_one.pop(c)
                # Major Injury
                if critical_fail_injury == "Major Injury":
                    if "Ageing With Grace" in c.perks:
                        c.current_speed -= 1
                        c.current_attack -= 1
                        c.current_defense -= 1
                    else:
                        c.current_speed -= 2
                        c.current_attack -= 2
                        c.current_defense -= 2
                # Minor Injury
                if critical_fail_injury == "Minor Injury":
                    c.current_speed -= 1
                    c.current_attack -= 1
                    c.current_defense -= 1
                combat_log.append(f"{c.name} suffers {critical_fail_injury}")
                combat_log.append(f"{c.name} Current Status - Speed: {c.current_speed} | Attack: {c.current_attack} | Defense: {c.current_defense}")

        # Side Two
        combat_side_two_initiative = []
        for c in combat_side_two:
            initiative_sum, _ = roll_2d20()
            combat_log.append(f"{c.name} rolls initiative: {_} + Speed {c.current_speed} = {initiative_sum + c.current_speed}")
            # Born Lucky Perk Check
            if ("Born Lucky" in c.perks) and (1 in _) and c.you_lucky == 0:
                c.you_lucky = 1
                initiative_sum, _ = roll_2d20()
                combat_log.append(f"{c.name} is lucky! They re-roll their initiative: {initiative_sum} + Speed {c.current_speed} = {initiative_sum + c.current_speed}")
            combat_side_two_initiative.append(initiative_sum + c.current_speed)
            # Crit Checks
            if 1 in _:
                c.crit_fail = 1
                combat_log.append(f"{c.name} rolls a Critical Fail!")
            if 20 in _:
                c.crit_success = 1
                combat_log.append(f"{c.name} rolls a Critical Success!")
            if 19 in _ and "Duelist T3" in c.perks:
                c.crit_success = 1
                combat_log.append(f"{c.name} rolls a Critical Success!")
            if 1 in _ and 20 in _:
                c.crit_fail = 0
                c.crit_success = 0
            # Thrown Projectile Specialist T3 - Free Throw
            if initiative_sum >= 30 and "Thrown Projectile Specialist T3" in c.perks and round_count == 1:
                # Random Target
                target = random.sample(combat_side_one, 1)[0]
                target_index = combat_side_one.index(target)
                combat_log.append(f"{c.name} throws a projectile at {target.name}")
                # Critical Strike
                if (c.crit_success == 1):
                    # Highest Speed
                    if((target.current_speed > target.current_attack) and (target.current_speed > target.current_defense)):
                        target.current_speed -= 2
                    # Highest Attack
                    elif((target.current_attack > target.current_speed) and (target.current_attack > target.current_defense)):
                        target.current_attack -= 2
                    # Highest Defense
                    elif((target.current_defense > target.current_speed) and (target.current_defense > target.current_attack)):
                        target.current_defense -= 2
                    bonus = 0
                    if "Sworn Sword T1" in target.perks:
                        bonus += 10
                    if "Sworn Sword T2" in target.perks:
                        bonus += 20
                    if "Sworn Sword T2" in target.perks:
                        bonus += 30
                    critical_strike_injury = secondary_injury_roll(ct, bonus)
                    # Critical Injury
                    if isinstance(critical_strike_injury, str) and "Critical Injury" in critical_strike_injury:
                        combat_log.append(f"{c.name} suffers {critical_strike_injury} and is taken out!")
                        combat_side_one.pop(target_index)
                        continue
                    # Major Injury
                    if critical_strike_injury == "Major Injury":
                        if "Ageing With Grace" in target.perks:
                            target.current_speed -= 1
                            target.current_attack -= 1
                            target.current_defense -= 1
                        else:
                            target.current_speed -= 2
                            target.current_attack -= 2
                            target.current_defense -= 2
                    # Minor Injury
                    if critical_strike_injury == "Minor Injury":
                        if "Bloodlust" in target.perks and target.bloodlusted == 0:
                            target.current_speed += 2
                            target.current_attack += 2
                            target.bloodlusted = 1
                        else:
                            target.current_speed -= 1
                            target.current_attack -= 1
                            target.current_defense -= 1
                    combat_log.append(f"{target.name} suffers {critical_strike_injury}")
                    combat_log.append(f"{target.name} Current Status - Speed: {target.current_speed} | Attack: {target.current_attack} | Defense: {target.current_defense}")
                # Status Check
                c.currently_engaging = 1
                target.combatants_faced += 1
                # Attack Roll
                attack_sum, _ = roll_3d5()
                attack_roll = ((attack_sum + c.current_attack) - target.current_defense)
                # Steel Tempest T3 - Double Attack
                if "Steel Tempest T3" in c.perks:
                    attack_roll = attack_roll * 2
                # Minimum Attack Roll - 1
                if attack_roll <= 0:
                    attack_roll = 1
                # Deduct from Target Morale
                target.current_morale -= attack_roll
                combat_log.append(f"{c.name} attacks {target.name} → Roll: {attack_sum} + Attack {c.current_attack} - Defense {target.current_defense} = {attack_roll}")
                combat_log.append(f"{target.name}'s morale drops to {target.current_morale}")
                combat_log.append(f"{target.name} Current Status - Speed: {target.current_speed} | Attack: {target.current_attack} | Defense: {target.current_defense}")
                # Berserker Rage Activated
                if ((target.current_morale <= 0) or (target.current_morale <= target.morale_threshold)) and "Berserker" in target.perks and target.berserked == 0:
                    target.current_morale += attack_roll
                    target.current_morale = (target.current_morale * 2)
                    target.berserked = 1
                    combat_log.append(f"{target.name} has gone berserk! Their morale has returned to: {target.current_morale}")
                # Target Knocked Out
                if (target.current_morale <= 0) or (target.current_morale <= target.morale_threshold) or (len(target.injuries) >= target.injury_threshold):
                    combat_log.append(f"{target.name} has been defeated!")
                    if(target.current_morale <= 0):
                        # Roll Primary Injury
                        bonus = 0
                        if "Sworn Sword T1" in target.perks:
                            bonus += 10
                        if "Sworn Sword T2" in target.perks:
                            bonus += 20
                        if "Sworn Sword T2" in target.perks:
                            bonus += 30
                        morale_injury_roll = primary_injury_roll(ct, bonus)
                        combat_log.append(f"{target.name} has been injured! - {morale_injury_roll}!")
                    combat_side_one.pop(target_index)
                # Terrifying Presence - Face One Opponent
                if ("Terrifying Presence T2" in target.perks) and (target.combatants_faced >= 1) and (len(combat_side_one)) == 1:
                    continue
            # Crit Fail & Miss
            if ((c.currently_engaging == 0) and c.crit_fail == 1):
                # Speed Highest
                if((c.current_speed > c.current_attack) and (c.current_speed > c.current_defense)):
                    c.current_speed -= 2
                # Attack Highest
                elif((c.current_attack > c.current_speed) and (c.current_attack > c.current_defense)):
                    c.current_attack -= 2
                # defense Highest
                elif((c.current_defense > c.current_speed) and (c.current_defense > c.current_attack)):
                    c.current_defense -= 2
                bonus = 0
                if "Sworn Sword T1" in c.perks:
                    bonus += 10
                if "Sworn Sword T2" in c.perks:
                    bonus += 20
                if "Sworn Sword T2" in c.perks:
                    bonus += 30
                critical_fail_injury = secondary_injury_roll(ct, bonus)
                # Critical Injury
                if isinstance(critical_fail_injury, str) and "Critical Injury" in critical_fail_injury:
                    combat_log.append(f"{c.name} suffers {critical_fail_injury} and is taken out!")
                    combat_side_two.pop(c)
                # Major Injury
                if critical_fail_injury == "Major Injury":
                    if "Ageing With Grace" in c.perks:
                        c.current_speed -= 1
                        c.current_attack -= 1
                        c.current_defense -= 1
                    else:
                        c.current_speed -= 2
                        c.current_attack -= 2
                        c.current_defense -= 2
                # Minor Injury
                if critical_fail_injury == "Minor Injury":
                    if "Bloodlust" in c.perks and c.bloodlusted == 0:
                        c.current_speed += 2
                        c.current_attack += 2
                        c.bloodlusted = 1
                    else:
                        c.current_speed -= 1
                        c.current_attack -= 1
                        c.current_defense -= 1
                combat_log.append(f"{c.name} suffers {critical_fail_injury}")
                combat_log.append(f"{c.name} Current Status - Speed: {c.current_speed} | Attack: {c.current_attack} | Defense: {c.current_defense}")

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

        # Check Initiative
        # Iterate Through Combat Side One
        i = 0
        while i < len(combat_side_one):
            c1 = combat_side_one[i]
            c1_init = combat_side_one_initiative[i]
            j = 0
            while j < len(combat_side_two):
                c2 = combat_side_two[j]
                c2_init = combat_side_two_initiative[j]
                # If Combatant Has Rolled Higher
                if ((c1_init > c2_init) and c1.currently_engaging == 0) or (c2.combatants_faced >= c2.max_combatants):
                    combat_log.append(f"{c1.name} attacks {c2.name}!")
                    # Critical Strike
                    if (c1.crit_success == 1):
                        # Speed Highest
                        if((c2.current_speed > c2.current_attack) and (c2.current_speed > c2.current_defense)):
                            c2.current_speed -= 2
                        # Attack Highest
                        elif((c2.current_attack > c2.current_speed) and (c2.current_attack > c2.current_defense)):
                            c2.current_attack -= 2
                        # defense Highest
                        elif((c2.current_defense > c2.current_speed) and (c2.current_defense > c2.current_attack)):
                            c2.current_defense -= 2
                        # Critical Strike Roll - Secondary Injury
                        bonus = 0
                        if "Sworn Sword T1" in c2.perks:
                            bonus += 10
                        if "Sworn Sword T2" in c2.perks:
                            bonus += 20
                        if "Sworn Sword T2" in c2.perks:
                            bonus += 30
                        if (("Valyrian Steel Sword" in c1.items) or ("Qohorik Steel Weapon" in c1.items)) and "Timeless Quality" in c1.perks:
                            bonus -= 20
                        critical_strike_injury = secondary_injury_roll(ct, bonus)
                        # Major / Critical Injury Re-roll - Shield Specialist T3 Perk
                        if (critical_strike_injury == "Major Injury" or critical_strike_injury == "Critical Injury") and "Shield Specialist T3" in c2.perks:
                            critical_strike_injury = secondary_injury_roll(ct, bonus)
                        # Critical Injury Inflicted
                        if isinstance(critical_strike_injury, str) and "Critical Injury" in critical_strike_injury:
                            combat_log.append(f"{c2.name} suffers {critical_strike_injury} and is taken out!")
                            combat_side_two.pop(i)
                            combat_side_two_initiative.pop(i)
                            continue
                        # Major Injury Taken
                        if critical_strike_injury == "Major Injury":
                            c2.major_injuries += 1
                        # Major Injury Check
                        if critical_strike_injury == "Major Injury" and c2.major_injuries > c2.major_injury_buff:
                            if "Ageing With Grace" in c2.perks:
                                c2.current_speed -= 1
                                c2.current_attack -= 1
                                c2.current_defense -= 1
                            else:
                                c2.current_speed -= 2
                                c2.current_attack -= 2
                                c2.current_defense -= 2
                        # Minor Injury
                        if critical_strike_injury == "Minor Injury":
                            if "Bloodlust" in c2.perks and c2.bloodlusted == 0:
                                c2.current_speed += 2
                                c2.current_attack += 2
                                c2.bloodlusted = 1
                            else:
                                c2.current_speed -= 1
                                c2.current_attack -= 1
                                c2.current_defense -= 1
                        combat_log.append(f"{c2.name} suffers {critical_strike_injury}")
                        combat_log.append(f"{c2.name} Current Status - Speed: {c2.current_speed} | Attack: {c2.current_attack} | Defense: {c2.current_defense}")
                    # Status Check
                    c1.currently_engaging = 1
                    c2.combatants_faced += 1
                    # Roll Attack
                    attack_sum, _ = roll_3d5()
                    # Timeless Quality Weapon Checks
                    if ("Timeless Quality" in c1.perks and ("Valyrian Steel Sword" in c1.items or "Qohorik Steel Weapon" in c1.items)) and ("Timeless Quality" in c2.perks and ("Valyrian Steel Armor" in c2.items or "Qohorik Armor" in c2.items)):
                        attack_roll = ((attack_sum + c1.current_attack) - c2.current_defense)
                    elif ("Timeless Quality" in c2.perks and ("Valyrian Steel Armor" in c2.items or "Qohorik Armor" in c2.items)):
                        attack_roll = ((attack_sum + c1.current_attack) - (c2.current_defense*2))
                    elif ("Timeless Quality" in c1.perks and ("Valyrian Steel Sword" in c1.items or "Qohorik Steel Weapon" in c1.items)):
                        attack_roll = ((attack_sum + c1.current_attack) - ((c2.current_defense + 1) // 2))
                    # Normal Attack
                    else:
                        attack_roll = ((attack_sum + c1.current_attack) - c2.current_defense)
                    # Steel Tempest T3 Perk Check
                    if "Steel Tempest T3" in c1.perks:
                        attack_roll = (attack_roll*2)
                    # Minimum Attack - 1
                    if attack_roll <= 0:
                        attack_roll = 1
                    # Deduct Attack From Morale
                    c2.current_morale -= attack_roll
                    combat_log.append(f"{c1.name} attacks {c2.name} → Roll: {attack_sum} + Attack {c1.current_attack} - Defense {c2.current_defense} = {attack_roll}")
                    combat_log.append(f"{c2.name}'s morale drops to {c2.current_morale}")
                    combat_log.append(f"{c2.name} Current Status - Speed: {c2.current_speed} | Attack: {c2.current_attack} | Defense: {c2.current_defense}")
                    # Going Berserk
                    if ((c2.current_morale <= 0) or (c2.current_morale <= c2.morale_threshold)) and "Berserker" in c2.perks and c2.berserked == 0:
                            c2.current_morale += attack_roll
                            c2.current_morale = (c2.current_morale * 2)
                            c2.berserked = 1
                            combat_log.append(f"{c2.name} has gone berserk! Their morale has returned to: {c2.current_morale}")
                    # Combatant Knocked Out
                    if (c2.current_morale <= 0) or (c2.current_morale <= c2.morale_threshold) or (len(c2.injuries) >= c2.injury_threshold):
                        combat_log.append(f"{c2.name} has been defeated!")
                        if(c2.current_morale <= 0):
                            # Roll Primary Injury
                            bonus = 0
                            if "Sworn Sword T1" in c2.perks:
                                bonus += 10
                            if "Sworn Sword T2" in c2.perks:
                                bonus += 20
                            if "Sworn Sword T2" in c2.perks:
                                bonus += 30
                            morale_injury_roll = primary_injury_roll(ct, bonus)
                            combat_log.append(f"{c2.name} has been injured! - {morale_injury_roll}!")
                        combat_side_two.pop()
                        combat_side_two_initiative.pop()
                        continue  # Don't increment j, as list has shifted
                    # Only Take One Attack - Terrifying Presence
                    if ("Terrifying Presence T2" in c2.perks) and (c2.combatants_faced >= 1) and (len(combat_side_two)) == 1:
                        continue
                j += 1
            i += 1
            # Crit Fail & Miss
            if (c1.currently_engaging == 0) and c1.crit_fail == 1:
                # Speed Highest
                if((c1.current_speed > c1.current_attack) and (c1.current_speed > c1.current_defense)):
                    c1.current_speed -= 2
                # Attack Highest
                elif((c1.current_attack > c1.current_speed) and (c1.current_attack > c1.current_defense)):
                    c1.current_attack -= 2
                # Defense Highest
                elif((c1.current_defense > c1.current_speed) and (c1.current_defense > c1.current_attack)):
                    c1.current_defense -= 2
                # Roll Critical Fail - Secondary Injury
                bonus = 0
                if "Sworn Sword T1" in c1.perks:
                    bonus += 10
                if "Sworn Sword T2" in c1.perks:
                    bonus += 20
                if "Sworn Sword T2" in c1.perks:
                    bonus += 30
                critical_fail_injury = secondary_injury_roll(ct, bonus)
                # Shield Specialist T3 Check
                if (critical_fail_injury == "Major Injury" or critical_fail_injury == "Critical Injury") and "Shield Specialist T3" in c1.perks:
                    critical_fail_injury = secondary_injury_roll(ct, bonus)
                # Critical Injury Knockout
                if isinstance(critical_fail_injury, str) and "Critical Injury" in critical_fail_injury:
                    combat_log.append(f"{c1.name} suffers {critical_fail_injury} and is taken out!")
                    combat_side_one.pop(i)
                    combat_side_one_initiative.pop(i)
                # Major Injury Check
                if critical_fail_injury == "Major Injury":
                    c1.major_injuries += 1
                # Major Injury
                if critical_fail_injury == "Major Injury" and c1.major_injuries > c1.major_injury_buff:
                    if "Ageing With Grace" in c1.perks:
                        c1.current_speed -= 1
                        c1.current_attack -= 1
                        c1.current_defense -= 1
                    else:
                        c1.current_speed -= 2
                        c1.current_attack -= 2
                        c1.current_defense -= 2
                # Minor Injury
                if critical_fail_injury == "Minor Injury":
                    if "Bloodlust" in c1.perks and c1.bloodlusted == 0:
                        c1.current_speed += 2
                        c1.current_attack += 2
                        c1.bloodlusted = 1
                    else:
                        c1.current_speed -= 1
                        c1.current_attack -= 1
                        c1.current_defense -= 1
                combat_log.append(f"{c1.name} suffers {critical_fail_injury}")
                combat_log.append(f"{c1.name} Current Status - Speed: {c1.current_speed} | Attack: {c1.current_attack} | Defense: {c1.current_defense}")

        # Iterate Through Combat Side Two
        i = 0
        while i < len(combat_side_two):
            c2 = combat_side_two[i]
            c2_init = combat_side_two_initiative[i]
            j = 0
            while j < len(combat_side_one):
                c1 = combat_side_one[j]
                c1_init = combat_side_one_initiative[j]
                # If Combatant Has Rolled Higher
                if ((combat_side_two_initiative[i] > combat_side_one_initiative[j]) and c2.currently_engaging == 0) or (combat_side_one[j].combatants_faced >= combat_side_one[j].max_combatants):
                    combat_log.append(f"{c2.name} attacks {c1.name}!")
                    # Critical Strike
                    if (combat_side_two[i].crit_success == 1):
                        # Speed Highest
                        if((combat_side_one[j].current_speed > combat_side_one[j].current_attack) and (combat_side_one[j].current_speed > combat_side_one[j].current_defense)):
                            combat_side_one[j].current_speed -= 2
                        # Attack Highest
                        elif((combat_side_one[j].current_attack > combat_side_one[j].current_speed) and (combat_side_one[j].current_attack > combat_side_one[j].current_defense)):
                            combat_side_one[j].current_attack -= 2
                        # Defense Highest
                        elif((combat_side_one[j].current_defense > combat_side_one[j].current_speed) and (combat_side_one[j].current_defense > combat_side_one[j].current_attack)):
                            combat_side_one[j].current_defense -= 2
                        # Critical Strike Roll - Secondary Injury
                        bonus = 0
                        if "Sworn Sword T1" in c1.perks:
                            bonus += 10
                        if "Sworn Sword T2" in c1.perks:
                            bonus += 20
                        if "Sworn Sword T2" in c1.perks:
                            bonus += 30
                        if (("Valyrian Steel Sword" in c2.items) or ("Qohorik Steel Weapon" in c2.items)) and "Timeless Quality" in c2.perks:
                            bonus -= 20
                        critical_strike_injury = secondary_injury_roll(ct, bonus)
                        # Shield Specialist T3 Perk Check
                        if (critical_strike_injury == "Major Injury" or critical_strike_injury == "Critical Injury") and "Shield Specialist T3" in combat_side_one[j].perks:
                            critical_strike_injury = secondary_injury_roll(ct, bonus)
                        # Critical Injury
                        if isinstance(critical_strike_injury, str) and "Critical Injury" in critical_strike_injury:
                            combat_log.append(f"{c1.name} suffers {critical_strike_injury} and is taken out!")
                            combat_side_one.pop(i)
                            combat_side_one_initiative.pop(i)
                        # Major Injury Check
                        if critical_strike_injury == "Major Injury":
                            combat_side_one[j].major_injuries += 1
                        # Major Injury
                        if critical_strike_injury == "Major Injury" and combat_side_one[j].major_injuries > combat_side_one[j].major_injury_buff:
                            if "Ageing With Grace" in c1.perks:
                                c1.current_speed -= 1
                                c1.current_attack -= 1
                                c1.current_defense -= 1
                            else:
                                c1.current_speed -= 2
                                c1.current_attack -= 2
                                c1.current_defense -= 2
                        # Minor Injury
                        if critical_strike_injury == "Minor Injury":
                            if "Bloodlust" in c1.perks and c1.bloodlusted == 0:
                                c1.current_speed += 2
                                c1.current_attack += 2
                                c1.bloodlusted = 1
                            else:
                                c1.current_speed -= 1
                                c1.current_attack -= 1
                                c1.current_defense -= 1
                            combat_log.append(f"{c1.name} suffers {critical_strike_injury}")
                            combat_log.append(f"{c1.name} Current Status - Speed: {c1.current_speed} | Attack: {c1.current_attack} | Defense: {c1.current_defense}")
                    # Status Check
                    c2.currently_engaging = 1
                    c1.combatants_faced += 1
                    # Roll Attack
                    attack_sum, _ = roll_3d5()
                    # Timeless Quality Perk Check
                    if ("Timeless Quality" in c2.perks and ("Valyrian Steel Sword" in c2.items or "Qohorik Steel Weapon" in c2.items)) and ("Timeless Quality" in c1.perks and ("Valyrian Steel Armor" in c1.items or "Qohorik Armor" in c1.items)):
                        attack_roll = ((attack_sum + c2.current_attack) - c1.current_defense)
                    elif ("Timeless Quality" in c1.perks and ("Valyrian Steel Armor" in c1.items or "Qohorik Armor" in c1.items)):
                        attack_roll = ((attack_sum + c2.current_attack) - (c1.current_defense*2))
                    elif ("Timeless Quality" in c2.perks and ("Valyrian Steel Sword" in c2.items or "Qohorik Steel Weapon" in c2.items)):
                        attack_roll = ((attack_sum + c2.current_attack) - ((c1.current_defense + 1) // 2))
                    # Normal Attack Roll
                    else:
                        attack_roll = ((attack_sum + c2.current_attack) - c1.current_defense)
                    # Steel Tempest T3 - Double Attack
                    if "Steel Tempest T3" in c1.perks:
                        attack_roll = (attack_roll*2)
                    # Minimum Attack = 1
                    if attack_roll <= 0:
                        attack_roll = 1
                    # Deduct Attack From Morale
                    c1.current_morale -= attack_roll
                    combat_log.append(f"{c2.name} attacks {c1.name} → Roll: {attack_sum} + Attack {c2.current_attack} - Defense {c1.current_defense} = {attack_roll}")
                    combat_log.append(f"{c1.name}'s morale drops to {c1.current_morale}")
                    combat_log.append(f"{c1.name} Current Status - Speed: {c1.current_speed} | Attack: {c1.current_attack} | Defense: {c1.current_defense}")
                    # Going Berserk
                    if ((c1.current_morale <= 0) or (c1.current_morale <= c1.morale_threshold)) and "Berserker" in c1.perks and c1.berserked == 0:
                            c1.current_morale += attack_roll
                            c1.current_morale = (c1.current_morale * 2)
                            c1.berserked = 1
                    # Combatant Knocked Out
                    if (c1.current_morale <= 0) or (c1.current_morale <= c1.morale_threshold) or (len(c1.injuries) >= c1.injury_threshold):
                        combat_log.append(f"{c1.name} has been defeated!")
                        if(c1.current_morale <= 0):
                            # Roll Primary Injury
                            bonus = 0
                            if "Sworn Sword T1" in c1.perks:
                                bonus += 10
                            if "Sworn Sword T2" in c1.perks:
                                bonus += 20
                            if "Sworn Sword T2" in c1.perks:
                                bonus += 30
                            morale_injury_roll = primary_injury_roll(ct, bonus)
                            combat_log.append(f"{c1.name} has been injured! - {morale_injury_roll}!")
                        combat_side_one.pop(j)
                        combat_side_one_initiative.pop(j)
                        continue  # Don't increment j, as list has shifted
                    # Take Only One Attack - Terrifying Presence T2 Perk Check
                    if ("Terrifying Presence T2" in c1.perks) and (c1.combatants_faced >= 1) and (len(combat_side_one)) == 1:
                        continue
                j += 1
            
            # Crit Fail & Miss
            if (c2.currently_engaging == 0) and c2.crit_fail == 1:
                # Speed Highest
                if((c2.current_speed > c2.current_attack) and (c2.current_speed > c2.current_defense)):
                    c2.current_speed -= 2
                # Attack Highest
                elif((c2.current_attack > c2.current_speed) and (c2.current_attack > c2.current_defense)):
                    c2.current_attack -= 2
                # defense Highest
                elif((c2.current_defense > c2.current_speed) and (c2.current_defense > c2.current_attack)):
                    c2.current_defense -= 2
                # Critical Fail Roll - Secondary Injury
                bonus = 0
                if "Sworn Sword T1" in c2.perks:
                    bonus += 10
                if "Sworn Sword T2" in c2.perks:
                    bonus += 20
                if "Sworn Sword T2" in c2.perks:
                    bonus += 30
                critical_fail_injury = secondary_injury_roll(ct, bonus)
                # Shield Specialist T3 - Perk Check
                if (critical_fail_injury == "Major Injury" or critical_fail_injury == "Critical Injury") and "Shield Specialist T3" in c2.perks:
                    critical_fail_injury = secondary_injury_roll(ct, bonus)
                # Critical Injury
                if isinstance(critical_fail_injury, str) and "Critical Injury" in critical_fail_injury:
                    combat_log.append(f"{c2.name} suffers {critical_fail_injury} and is taken out!")
                    combat_side_two.pop(i)
                    combat_side_two_initiative.pop(i)
                # Major Injury
                if critical_fail_injury == "Major Injury":
                    if "Ageing With Grace" in c2.perks:
                        c2.current_speed -= 1
                        c2.current_attack -= 1
                        c2.current_defense -= 1
                    else:
                        c2.current_speed -= 2
                        c2.current_attack -= 2
                        c2.current_defense -= 2
                # Minor Injury
                if critical_fail_injury == "Minor Injury":
                    if "Bloodlust" in c2.perks and c2.bloodlusted == 0:
                        c2.current_speed += 2
                        c2.current_attack += 2
                        c2.bloodlusted = 1
                    else:
                        c2.current_speed -= 1
                        c2.current_attack -= 1
                        c2.current_defense -= 1
                combat_log.append(f"{c2.name} suffers {critical_fail_injury}")
                combat_log.append(f"{c2.name} Current Status - Speed: {c2.current_speed} | Attack: {c2.current_attack} | Defense: {c2.current_defense}")
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
            combat_log.append("This round has ended in a stalemate, neither side have made progress.")

        # End Of Round
        # Print Round
        combat_log.append("==============================================================")
        combat_log_string(combat_log)
        combat_log = []
        # Reset Initiative
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
        combat_log.append("Side Two has won this duel!")
        combat_log_string(combat_log)
        combat_log = []

    if len(combat_side_two) == 0:
        combat_log.append("Side One has won this duel!")
        combat_log_string(combat_log)
        combat_log = []
    
######################################################################################################
# Combat Scenario - Ranged vs Ranged
######################################################################################################

def ranged_ranged(side1, side2, ct):

    # Combat Log
    combat_log = []
    round_count = 0  

    # Side Initialization
    combat_side_one = side_initialization(side1)
    combat_side_two = side_initialization(side2)
    # Stat Initialization
    for c in combat_side_one + combat_side_two:
        ranged_initialization(c)

    # Log fighters and their teams before combat starts
    combat_log.append("==============================================================")
    if not combat_log:
        combat_log.append("Side 1")
        for c in combat_side_one:
            combat_log.append(
                f"  {c.name} - Speed: {c.current_speed} | Attack: {c.current_attack} | Defense: {c.current_defense} | Morale: {c.current_morale} | Perks: {c.perks} | Injury Malus: {c.injuries} | Items: {c.items}"
            )
        combat_log.append("Side 2")
        for c in combat_side_two:
            combat_log.append(
                f"  {c.name} - Speed: {c.current_speed} | Attack: {c.current_attack} | Defense: {c.current_defense} | Morale: {c.current_morale} | Perks: {c.perks} | Injury Malus: {c.injuries} | Items: {c.items}"
            )
    combat_log.append("==============================================================")

    # Battlefield Champion T3 Check
    # Side One
    bc3_count = 0
    bc3_check = 0
    for c in combat_side_one:
        if "Battlefield Champion T3" in c.perks:
            for d in combat_side_one:
                if(bc3_count != bc3_check):
                    d.current_morale += 7
                bc3_check +=1
            combat_log.append(f"The presence of the Battlefield Champion {c.name} boosts the morale of the men around them!")
        bc3_count += 1
        
    # Side Two
    bc3_count = 0
    bc3_check = 0
    for e in combat_side_two:
        if "Battlefield Champion T3" in e.perks:
            for f in combat_side_one:
                if(bc3_count != bc3_check):
                    f.current_morale += 7
                bc3_check +=1
            combat_log.append(f"The presence of the Battlefield Champion {e.name} boosts the morale of the men around them!")
        bc3_count += 1

    while len(combat_side_one) > 0 and len(combat_side_two) > 0:

        round_count += 1
        combat_log.append("==============================================================")

        if (len(combat_side_one) == 1) and len(combat_side_two) > 1 and ("Terrifying Presence T1" in combat_side_one[0].perks) and (combat_side_one[0].imposed_presence == 0):
            combat_side_one[0].imposed_presence = 1
            for c in combat_side_two:
                c.morale_threshold += 10
            combat_log.append(f"The terrifying presence of {combat_side_one[0].name} strikes fear into the heart of their enemies!")
        if (len(combat_side_two) == 1) and len(combat_side_one) > 1 and ("Terrifying Presence T1" in combat_side_two[0].perks) and (combat_side_two[0].imposed_presence == 0):
            combat_side_two[0].imposed_presence = 1
            for c in combat_side_one:
                c.morale_threshold += 10
            combat_log.append(f"The terrifying presence of {combat_side_two[0].name} strikes fear into the heart of their enemies!")
        if (len(combat_side_one) == 1) and len(combat_side_two) > 1 and ("Terrifying Presence T2" in combat_side_one[0].perks) and (combat_side_one[0].imposed_presence == 0):
            combat_side_one[0].imposed_presence = 1
            for c in combat_side_two:
                c.morale_threshold += 15
            combat_log.append(f"The terrifying presence of {combat_side_one[0].name} strikes fear into the heart of their enemies!")
        if (len(combat_side_two) == 1) and len(combat_side_one) > 1 and ("Terrifying Presence T2" in combat_side_two[0].perks) and (combat_side_two[0].imposed_presence == 0):
            combat_side_two[0].imposed_presence = 1
            for c in combat_side_one:
                c.morale_threshold += 15
            combat_log.append(f"The terrifying presence of {combat_side_two[0].name} strikes fear into the heart of their enemies!")
        # Roll Initiative
        # Side One
        combat_side_one_initiative = []
        for c in combat_side_one:
            initiative_sum, _ = roll_2d20()
            combat_log.append(f"{c.name} rolls initiative: {_} + Speed {c.current_speed} = {initiative_sum + c.current_speed}")
            if ("Born Lucky" in c.perks) and (1 in _) and c.you_lucky == 0:
                c.you_lucky = 1
                initiative_sum, _ = roll_2d20()
                combat_log.append(f"{c.name} is lucky! They re-roll their initiative: {initiative_sum} + Speed {c.current_speed} = {initiative_sum + c.current_speed}")
            combat_side_one_initiative.append(initiative_sum + c.current_speed)
            if 1 in _:
                c.crit_fail = 1
                combat_log.append(f"{c.name} rolls a Critical Fail!")
            if 20 in _:
                c.crit_success = 1
                combat_log.append(f"{c.name} rolls a Critical Success!")
            if 1 in _ and 20 in _:
                c.crit_fail = 0
                c.crit_success = 0
        # Side Two
        combat_side_two_initiative = []
        for c in combat_side_two:
            initiative_sum, _ = roll_2d20()
            combat_log.append(f"{c.name} rolls initiative: {_} + Speed {c.current_speed} = {initiative_sum + c.current_speed}")
            if ("Born Lucky" in c.perks) and (1 in _) and c.you_lucky == 0:
                c.you_lucky = 1
                initiative_sum, _ = roll_2d20()
                combat_log.append(f"{c.name} is lucky! They re-roll their initiative: {initiative_sum} + Speed {c.current_speed} = {initiative_sum + c.current_speed}")
            combat_side_two_initiative.append(initiative_sum + c.current_speed)
            if 1 in _:
                c.crit_fail = 1
                combat_log.append(f"{c.name} rolls a Critical Fail!")
            if 20 in _:
                c.crit_success = 1
                combat_log.append(f"{c.name} rolls a Critical Success!")
            if 1 in _ and 20 in _:
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
                    combat_log.append(f"{c1.name} attacks {c2.name}!")
                    # Critical Strike
                    if (combat_side_one[i].crit_success == 1):
                        if((c2.current_speed > c2.current_attack) and (c2.current_speed > c2.current_defense)):
                            c2.current_speed -= 2
                        elif((c2.current_attack > c2.current_speed) and (c2.current_attack > c2.current_defense)):
                            c2.current_attack -= 2
                        elif((c2.current_defense > c2.current_speed) and (c2.current_defense > c2.current_attack)):
                            c2.current_defense -= 2
                        bonus = 0
                        critical_strike_injury = secondary_injury_roll(ct, bonus)
                        if isinstance(critical_strike_injury, str) and "Critical Injury" in critical_strike_injury:
                            combat_log.append(f"{c2.name} suffers {critical_strike_injury} and is taken out!")
                            combat_side_two.pop(i)
                            combat_side_two_initiative.pop(i)
                        if critical_strike_injury == "Major Injury":
                            if "Ageing With Grace" in c2.perks:
                                c2.current_speed -= 1
                                c2.current_attack -= 1
                                c2.current_defense -= 1
                            else:
                                c2.current_speed -= 2
                                c2.current_attack -= 2
                                c2.current_defense -= 2
                        if critical_strike_injury == "Minor Injury":
                            if "Bloodlust" in c2.perks and c2.bloodlusted == 0:
                                c2.current_speed += 2
                                c2.current_attack += 2
                                c2.bloodlusted = 1
                            else:
                                c2.current_speed -= 1
                                c2.current_attack -= 1
                                c2.current_defense -= 1
                        combat_log.append(f"{c2.name} suffers {critical_strike_injury}")
                        combat_log.append(f"{c2.name} Current Status - Speed: {c2.current_speed} | Attack: {c2.current_attack} | Defense: {c2.current_defense}")
                    c1.currently_engaging = 1
                    c2.combatants_faced += 1
                    attack_sum, _ = roll_3d5()
                    attack_roll = ((attack_sum + c1.current_attack) - c2.current_defense)
                    if attack_roll <= 0:
                        attack_roll = 1
                    c2.current_morale -= attack_roll
                    combat_log.append(f"{c1.name} attacks {c2.name} → Roll: {attack_sum} + Attack {c1.current_attack} - Defense {c2.current_defense} = {attack_roll}")
                    combat_log.append(f"{c2.name}'s morale drops to {c2.current_morale}")
                    combat_log.append(f"{c2.name} Current Status - Speed: {c2.current_speed} | Attack: {c2.current_attack} | Defense: {c2.current_defense}")
                    if ((c2.current_morale <= 0) or (c2.current_morale <= c2.morale_threshold)) and "Berserker" in c2.perks and c2.berserked == 0:
                            c2.current_morale += attack_roll
                            c2.current_morale = (c2.current_morale * 2)
                            c2.berserked = 1
                            combat_log.append(f"{c2.name} has gone berserk! Their morale has returned to: {c2.current_morale}")
                    if (c2.current_morale <= 0) or (c2.current_morale <= c2.morale_threshold) or (len(c2.injuries) >= c2.injury_threshold):
                        combat_log.append(f"{c2.name} has been defeated!")
                        if(c2.current_morale <= 0):
                            # Roll Primary Injury
                            bonus = 0
                            morale_injury_roll = primary_injury_roll(ct, bonus)
                            combat_log.append(f"{c2.name} has been injured! - {morale_injury_roll}!")
                        combat_side_two.pop(j)
                        combat_side_two_initiative.pop(j)
                        continue  # Don't increment j, as list has shifted
                    if ("Terrifying Presence T2" in c2.perks) and (c2.combatants_faced >= 1) and (len(combat_side_two)) == 1:
                        continue
                j += 1
            i += 1
            if (c1.currently_engaging == 0) and c1.crit_fail == 1:
                if((c1.current_speed > c1.current_attack) and (c1.current_speed > c1.current_defense)):
                    c1.current_speed -= 2
                elif((c1.current_attack > c1.current_speed) and (c1.current_attack > c1.current_defense)):
                    c1.current_attack -= 2
                elif((c1.current_defense > c1.current_speed) and (c1.current_defense > c1.current_attack)):
                    c1.current_defense -= 2
                bonus = 0
                critical_fail_injury = secondary_injury_roll(ct, bonus)
                if isinstance(critical_fail_injury, str) and "Critical Injury" in critical_fail_injury:
                    combat_log.append(f"{c1.name} suffers {critical_fail_injury} and is taken out!")
                    combat_side_one.pop(i)
                    combat_side_one_initiative.pop(i)
                if critical_fail_injury == "Major Injury":
                    if "Ageing With Grace" in c1.perks:
                        c1.current_speed -= 1
                        c1.current_attack -= 1
                        c1.current_defense -= 1
                    else:
                        c1.current_speed -= 2
                        c1.current_attack -= 2
                        c1.current_defense -= 2
                if critical_fail_injury == "Minor Injury":
                    if "Bloodlust" in c1.perks and c1.bloodlusted == 0:
                        c1.current_speed += 2
                        c1.current_attack += 2
                        c1.bloodlusted = 1
                    else:
                        c1.current_speed -= 1
                        c1.current_attack -= 1
                        c1.current_defense -= 1
                combat_log.append(f"{c1.name} suffers {critical_fail_injury}")
                combat_log.append(f"{c1.name} Current Status - Speed: {c1.current_speed} | Attack: {c1.current_attack} | Defense: {c1.current_defense}")

        # Iterate Through Combat Side Two
        i = 0
        while i < len(combat_side_two):
            c2 = combat_side_two[i]
            j = 0
            while j < len(combat_side_one):
                c1 = combat_side_one[j]
                # If Combatant Has Rolled Higher
                if ((combat_side_two_initiative[i] > 30) and c2.currently_engaging == 0) or (combat_side_one[j].combatants_faced >= combat_side_one[j].max_combatants):
                    combat_log.append(f"{c2.name} attacks {c1.name}!")
                    # Critical Strike
                    if (c2.crit_success == 1):
                        if((c1.current_speed > c1.current_attack) and (c1.current_speed > c1.current_defense)):
                            c1.current_speed -= 2
                        elif((c1.current_attack > c1.current_speed) and (c1.current_attack > c1.current_defense)):
                            c1.current_attack -= 2
                        elif((c1.current_defense > c1.current_speed) and (c1.current_defense > c1.current_attack)):
                            c1.current_defense -= 2
                        bonus = 0
                        critical_strike_injury = secondary_injury_roll(ct, bonus)
                        if isinstance(critical_strike_injury, str) and "Critical Injury" in critical_strike_injury:
                            combat_log.append(f"{c1.name} suffers {critical_strike_injury} and is taken out!")
                            combat_side_one.pop(i)
                            combat_side_one_initiative.pop(i)
                        if critical_strike_injury == "Major Injury":
                            if "Ageing With Grace" in c1.perks:
                                c1.current_speed -= 1
                                c1.current_attack -= 1
                                c1.current_defense -= 1
                            else:
                                c1.current_speed -= 2
                                c1.current_attack -= 2
                                c1.current_defense -= 2
                        if critical_strike_injury == "Minor Injury":
                            if "Bloodlust" in c1.perks and c1.bloodlusted == 0:
                                c1.current_speed += 2
                                c1.current_attack += 2
                                c1.bloodlusted = 1
                            else:
                                c1.current_speed -= 1
                                c1.current_attack -= 1
                                c1.current_defense -= 1
                        combat_log.append(f"{c1.name} suffers {critical_strike_injury}")
                        combat_log.append(f"{c1.name} Current Status - Speed: {c1.current_speed} | Attack: {c1.current_attack} | Defense: {c1.current_defense}")
                    # One Combatant Only
                    c2.currently_engaging = 1
                    c1.combatants_faced += 1
                    # Roll Attack
                    attack_sum, _ = roll_3d5()
                    attack_roll = ((attack_sum + c2.current_attack) - c1.current_defense)
                    if attack_roll <= 0:
                        attack_roll = 1
                    c1.current_morale -= attack_roll
                    combat_log.append(f"{c2.name} attacks {c1.name} → Roll: {attack_sum} + Attack {c2.current_attack} - Defense {c1.current_defense} = {attack_roll}")
                    combat_log.append(f"{c1.name}'s morale drops to {c1.current_morale}")
                    combat_log.append(f"{c1.name} Current Status - Speed: {c1.current_speed} | Attack: {c1.current_attack} | Defense: {c1.current_defense}")
                    if ((c1.current_morale <= 0) or (c1.current_morale <= c1.morale_threshold)) and "Berserker" in c1.perks and c1.berserked == 0:
                            c1.current_morale += attack_roll
                            c1.current_morale = (c1.current_morale * 2)
                            c1.berserked = 1
                            combat_log.append(f"{c1.name} has gone berserk! Their morale has returned to: {c1.current_morale}")
                    if (c1.current_morale <= 0) or (c1.current_morale <= c1.morale_threshold) or (len(c1.injuries) >= c1.injury_threshold):
                        combat_log.append(f"{c1.name} has been defeated!")
                        if(c1.current_morale <= 0):
                            # Roll Primary Injury
                            bonus = 0
                            morale_injury_roll = primary_injury_roll(ct, bonus)
                            combat_log.append(f"{c1.name} has been injured! - {morale_injury_roll}!")
                        combat_side_one.pop(j)
                        combat_side_one_initiative.pop(j)
                        continue  # Don't increment j, as list has shifted
                    if ("Terrifying Presence T2" in c1.perks) and (c1.combatants_faced >= 1) and (len(combat_side_one)) == 1:
                        continue
                j += 1
            
            if (c2.currently_engaging == 0) and c2.crit_fail == 1:
                if((c2.current_speed > c2.current_attack) and (c2.current_speed > c2.current_defense)):
                    c2.current_speed -= 2
                elif((c2.current_attack > c2.current_speed) and (c2.current_attack > c2.current_defense)):
                    c2.current_attack -= 2
                elif((c2.current_defense > c2.current_speed) and (c2.current_defense > c2.current_attack)):
                    c2.current_defense -= 2
                bonus = 0
                critical_fail_injury = secondary_injury_roll(ct, bonus)
                if isinstance(critical_fail_injury, str) and "Critical Injury" in critical_fail_injury:
                    combat_log.append(f"{c2.name} suffers {critical_fail_injury} and is taken out!")
                    combat_side_two.pop(i)
                    combat_side_two_initiative.pop(i)
                if critical_fail_injury == "Major Injury":
                    if "Ageing With Grace" in c2.perks:
                        c2.current_speed -= 1
                        c2.current_attack -= 1
                        c2.current_defense -= 1
                    else:
                        c2.current_speed -= 2
                        c2.current_attack -= 2
                        c2.current_defense -= 2
                if critical_fail_injury == "Minor Injury":
                    if "Bloodlust" in c2.perks and c2.bloodlusted == 0:
                        c2.current_speed += 2
                        c2.current_attack += 2
                        c2.bloodlusted = 1
                    else:
                        c2.current_speed -= 1
                        c2.current_attack -= 1
                        c2.current_defense -= 1
                combat_log.append(f"{c2.name} suffers {critical_fail_injury}")
                combat_log.append(f"{c2.name} Current Status - Speed: {c2.current_speed} | Attack: {c2.current_attack} | Defense: {c2.current_defense}")
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
            combat_log.append("This round has ended in a stalemate, neither side have made progress.")

        # End Of Round
        # Print Round
        combat_log.append("==============================================================")
        combat_log_string(combat_log)
        combat_log = []
        # Reset Initiative
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
        combat_log.append("Side Two has won this duel!")
        combat_log_string(combat_log)
        combat_log = []

    if len(combat_side_two) == 0:
        combat_log.append("Side One has won this duel!")
        combat_log_string(combat_log)
        combat_log = []


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
# side1_data = [
#     {"name": "Arya", "age": 18, "perks": ["Born Lucky"], "injuries": [], "injury_threshold": 4, "morale_threshold": 15},
#     {"name": "Brienne", "age": 32, "perks": ["Sworn Sword T2"], "injuries": [], "injury_threshold": 4, "morale_threshold": 15}
# ]
# # Side 2
# side2_data = [
#     {"name": "Jaime", "age": 35, "perks": ["Blade Specialist T3"], "injuries": [], "injury_threshold": 4, "morale_threshold": 15},
#     {"name": "Bronn", "age": 40, "perks": ["Marksman T1"], "injuries": [], "injury_threshold": 4, "morale_threshold": 15}
# ]

# Combat Type
# combat_data = "Live Melee vs Melee"
# combat_data = "Live Ranged vs Melee" - Side 1 Must Be Ranged
# combat_data = "Live Ranged vs Ranged"
# combat_data = "Blunted Melee vs Melee"
# combat_data = "Blunted Ranged vs Melee" - Side 1 Must Be Ranged
# combat_data = "Blunted Ranged vs Ranged"

# Combat Initialization
# if __name__ == "__main__":
    # combat_data = "Live Melee vs Melee"
    # combat_initialization(combat_data, side1_data, side2_data)          # Initialize Combat

    # Pause at the end so output is visible if run from double-click or IDE
    # input("\nPress Enter to exit...")

######################################################################################################
# CLI Interface
######################################################################################################

while True:
    # Initialize Sides
    side1_data = []
    side2_data = []
    # Print Menu
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    print("           Crowned Stag Duel Rework")
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    print("\n1: Battlefield Duel Seeking")
    print("2: Melee vs Melee")
    print("3: Ranged vs Melee")
    print("4: Ranged vs Ranged\n")
    # Select Option
    choice = input("Select an option (1-4): ").strip()
    # Battlefield Seeking
    if choice == "1":
        # Target
        print("\nSide One:\n")
        print(f"Target: ")
        name = input("Name: ").strip()
        age = input("Age: ").strip()
        perks = input("Perks (Blade Specialist T3, Born Lucky): ").strip()
        injuries = input("Injuries: ").strip()
        injury_threshold = input("Injury Threshold (Default: 4): ").strip()
        morale_threshold = input("Morale Threshold (Default: 15): ").strip()
        items = input("Items (Valyrian Steel Sword): ").strip()
        # Parse injuries as maluses for speed, attack, defense
        injury_maluses = [int(x.strip()) for x in injuries.split(",") if x.strip()] if injuries else []
        # Pad to 3 values if needed
        while len(injury_maluses) < 3:
            injury_maluses.append(0)
        target = Character(
            name,
            int(age) if age else 18,
            [p.strip() for p in perks.split(",") if p.strip()] if perks else [],
            injury_maluses,
            int(injury_threshold) if injury_threshold else 4,
            int(morale_threshold) if morale_threshold else 15,
            [it.strip() for it in items.split(",") if it.strip()] if items else []
        )
        # Initiator
        print("\nSide Two:\n")
        print(f"Seeker: ")
        name = input("Name: ").strip()
        age = input("Age: ").strip()
        perks = input("Perks (Blade Specialist T3, Born Lucky): ").strip()
        injuries = input("Injuries: ").strip()
        injury_threshold = input("Injury Threshold (Default: 4): ").strip()
        morale_threshold = input("Morale Threshold (Default: 15): ").strip()
        items = input("Items (Valyrian Steel Sword): ").strip()
        # Parse injuries as maluses for speed, attack, defense
        injury_maluses = [int(x.strip()) for x in injuries.split(",") if x.strip()] if injuries else []
        # Pad to 3 values if needed
        while len(injury_maluses) < 3:
            injury_maluses.append(0)
        initiator = Character(
            name,
            int(age) if age else 18,
            [p.strip() for p in perks.split(",") if p.strip()] if perks else [],
            [i.strip() for i in injuries.split(",") if i.strip()] if injuries else [],
            int(injury_threshold) if injury_threshold else 4,
            int(morale_threshold) if morale_threshold else 15,
            [it.strip() for it in items.split(",") if it.strip()] if items else []
        )
        # Combat Seeking Roll
        combat_seeking(target, initiator)
    # Combat
    elif choice == "2" or choice == "3" or choice == "4":
        print("\n1: Steel Weapons")
        print("2: Blunted Weapons\n")
        combat_type = input("Select an option (1-2): ").strip()
        if combat_type == "1" or combat_type == "2":
            print("\n1: Test Run - 1")
            print("2: Test Run - 10000\n")
            test_runs = input("Select an option (1-2): ").strip()
            if test_runs == "1" or test_runs == "2":
                side_one = input("\nEnter # of Combatants - Side 1: ").strip()
                side_two = input("Enter # of Combatants - Side 2: ").strip()
                try:
                    side_one_int = int(side_one)
                    side_two_int = int(side_two)
                    if side_one_int > 0 and side_two_int > 0:
                        s1 = 0
                        s2 = 0
                        while s1 < side_one_int:
                            if s1 == 0:
                                print("\nSide One:\n")
                            print(f"Combatant {s1 + 1}")
                            name = input("Name: ").strip()
                            age = input("Age: ").strip()
                            perks = input("Perks (Blade Specialist T3, Born Lucky): ").strip()
                            injuries = input("Injuries: ").strip()
                            injury_threshold = input("Injury Threshold (Default: 4): ").strip()
                            morale_threshold = input("Morale Threshold (Default: 15): ").strip()
                            items = input("Items (Valyrian Steel Sword): ").strip()
                            # Parse injuries as maluses for speed, attack, defense
                            injury_maluses = [int(x.strip()) for x in injuries.split(",") if x.strip()] if injuries else []
                            # Pad to 3 values if needed
                            while len(injury_maluses) < 3:
                                injury_maluses.append(0)
                            side1_data.append({
                                "name": name,
                                "age": int(age) if age else 18,
                                "perks": [p.strip() for p in perks.split(",") if p.strip()] if perks else [],
                                "injuries": [i.strip() for i in injuries.split(",") if i.strip()] if injuries else [],
                                "injury_threshold": int(injury_threshold) if injury_threshold else 4,
                                "morale_threshold": int(morale_threshold) if morale_threshold else 15,
                                "items": [it.strip() for it in items.split(",") if it.strip()] if items else []
                            })
                            s1 += 1
                        while s2 < side_two_int:
                            if s2 == 0:
                                print("\nSide Two:\n")
                            print(f"Combatant {s2 + 1}")
                            name = input("Name: ").strip()
                            age = input("Age: ").strip()
                            perks = input("Perks (Blade Specialist T3, Born Lucky): ").strip()
                            injuries = input("Injuries: ").strip()
                            injury_threshold = input("Injury Threshold (Default: 4): ").strip()
                            morale_threshold = input("Morale Threshold (Default: 15): ").strip()
                            items = input("Items (Valyrian Steel Sword): ").strip()
                            # Parse injuries as maluses for speed, attack, defense
                            injury_maluses = [int(x.strip()) for x in injuries.split(",") if x.strip()] if injuries else []
                            # Pad to 3 values if needed
                            while len(injury_maluses) < 3:
                                injury_maluses.append(0)
                            side2_data.append({
                                "name": name,
                                "age": int(age) if age else 18,
                                "perks": [p.strip() for p in perks.split(",") if p.strip()] if perks else [],
                                "injuries": [i.strip() for i in injuries.split(",") if i.strip()] if injuries else [],
                                "injury_threshold": int(injury_threshold) if injury_threshold else 4,
                                "morale_threshold": int(morale_threshold) if morale_threshold else 15,
                                "items": [it.strip() for it in items.split(",") if it.strip()] if items else []
                            })
                            s2 += 1
                        # default
                        combat_data = "Live Melee vs Melee"
                        if choice == "2" and combat_type == "1":
                            combat_data = "Live Melee vs Melee"
                        if choice == "2" and combat_type == "2":
                            combat_data = "Blunted Melee vs Melee"
                        if choice == "3" and combat_type == "1":
                            combat_data = "Live Ranged vs Melee"
                        if choice == "3" and combat_type == "2":
                            combat_data = "Blunted Ranged vs Melee"
                        if choice == "4" and combat_type == "1":
                            combat_data = "Live Ranged vs Ranged"
                        if choice == "4" and combat_type == "2":
                            combat_data = "Blunted Ranged vs Ranged"
                        if test_runs == "1":
                            combat_initialization(combat_data, side1_data, side2_data)
                        if test_runs == "2":
                            i = 0
                            while i < 10000:
                                combat_initialization(combat_data, side1_data, side2_data)
                                i = i + 1
                    else:
                        print("Invalid amount.")
                except ValueError:
                    print("Invalid amount.")
            else:
                print("Invalid option.")
        else:
            print("Invalid option.")
    else:
        print("Invalid option.")
    