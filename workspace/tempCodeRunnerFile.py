# Melee vs Melee - Live
def live_melee_melee(side1, side2):
    # Initialize Sides
    combat_side_one = side_initialization(side1)
    combat_side_two = side_initialization(side2)
    # Initialize Characters
    for c in combat_side_one:
        melee_initialization(c)
    for c in combat_side_two:
        melee_initialization(c)
    # Melee vs Melee Combat
    round_num = 1
    while combat_side_one and combat_side_two:
        print(f"\n--- Round {round_num} ---\n", flush=True)
        # Roll Initiative for all alive characters
        initiatives = []
        for c in combat_side_one:
            roll, rolls = roll_2d20()
            initiatives.append((roll + c.current_speed, rolls, c, "side_one"))
            print(f"{c.name} initiative: {roll + c.current_speed} (rolls: {rolls})", flush=True)
        for c in combat_side_two:
            roll, rolls = roll_2d20()
            initiatives.append((roll + c.current_speed, rolls, c, "side_two"))
            print(f"{c.name} initiative: {roll + c.current_speed} (rolls: {rolls})", flush=True)
        # Sort by initiative descending
        initiatives.sort(reverse=True, key=lambda x: x[0])
        # Track alive by name for quick lookup
        alive_one = {c.name: c for c in combat_side_one}
        alive_two = {c.name: c for c in combat_side_two}
        # Each character acts in initiative order
        for _, _, attacker, side in initiatives:
            # Skip if attacker has already been defeated this round
            if side == "side_one" and attacker.name not in alive_one:
                continue
            if side == "side_two" and attacker.name not in alive_two:
                continue
            # Find a target on the opposing side
            if side == "side_one" and alive_two:
                # Target: lowest morale enemy
                target = min(alive_two.values(), key=lambda t: t.current_morale)
            elif side == "side_two" and alive_one:
                target = min(alive_one.values(), key=lambda t: t.current_morale)
            else:
                continue  # No valid targets
            # Attack!
            attack_result = roll_3d5()
            attack_roll = attack_result[0]
            attack_rolls = attack_result[1]
            attack_value = (attack_roll + attacker.current_attack) - target.current_defense
            target.current_morale -= attack_value
            # Prevent morale from dropping below zero
            if target.current_morale < 0:
                target.current_morale = 0
            print(f"{attacker.name} attacks {target.name} for {attack_value} (rolls: {attack_rolls}) - {target.name} morale now: {target.current_morale}", flush=True)
            if target.current_morale <= target.morale_threshold:
                if side == "side_one":
                    if target.name in alive_two:
                        del alive_two[target.name]
                        print(f"{target.name} has been defeated and is removed from combat!", flush=True)
                else:
                    if target.name in alive_one:
                        del alive_one[target.name]
                        print(f"{target.name} has been defeated and is removed from combat!", flush=True)
        # Remove defeated characters from combat sides
        combat_side_one = [c for c in combat_side_one if c.name in alive_one]
        combat_side_two = [c for c in combat_side_two if c.name in alive_two]
        # Check for Remaining Characters
        if not combat_side_one:
            print("Combat Side One has been defeated!", flush=True)
            return "Side Two Wins"
        if not combat_side_two:
            print("Combat Side Two has been defeated!", flush=True)
            return "Side One Wins"
        round_num += 1
