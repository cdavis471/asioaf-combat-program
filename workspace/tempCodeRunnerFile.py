elif result == "Critical Injury":
            # Roll on the Critical Injury Table for specific injury
            roll = random.randint(1, 20)
            injury_name, effect_func = CRITICAL_INJURY_TABLE[roll]
            log.append(f"{defender.name} suffers a **Critical Injury** – {injury_name}!")
            defender.injuries_count += 1
            effect_func(defender)
            if injury_name == "Death":
                defender.current_morale = 0