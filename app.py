import streamlit as st
import math

def calculate_chain_heal_healing(total_healing_power, spell_type="Chain Heal"):
    """Calculate Chain Heal healing values based on +healing power and spell type"""
    base_min = 567
    base_max = 646
    base_avg = (base_min + base_max) / 2
    
    # Chain Heal gets 55.36% of +healing power
    healing_bonus = total_healing_power * 0.5536
    
    # Calculate base heal values
    first_heal_min = base_min + healing_bonus
    first_heal_max = base_max + healing_bonus
    first_heal_avg = base_avg + healing_bonus
    
    # Calculate jump healing based on spell type
    if spell_type == "Chain Heal":
        # T2 bonus: loses 20% per jump (80% effectiveness)
        second_heal_min = first_heal_min * 0.8
        second_heal_max = first_heal_max * 0.8
        second_heal_avg = first_heal_avg * 0.8
        
        third_heal_min = second_heal_min * 0.8
        third_heal_max = second_heal_max * 0.8
        third_heal_avg = second_heal_avg * 0.8
    else:  # Chain Heal w/o T2 bonus
        # Without T2 bonus: loses 50% per jump
        second_heal_min = first_heal_min * 0.5
        second_heal_max = first_heal_max * 0.5
        second_heal_avg = first_heal_avg * 0.5
        
        third_heal_min = second_heal_min * 0.5
        third_heal_max = second_heal_max * 0.5
        third_heal_avg = second_heal_avg * 0.5
    
    # Calculate total healing (all 3 jumps)
    total_min = first_heal_min + second_heal_min + third_heal_min
    total_max = first_heal_max + second_heal_max + third_heal_max
    total_avg = first_heal_avg + second_heal_avg + third_heal_avg
    
    return {
        'total_min': total_min,
        'total_max': total_max,
        'total_avg': total_avg,
        'first_jump': {'min': first_heal_min, 'max': first_heal_max, 'avg': first_heal_avg},
        'second_jump': {'min': second_heal_min, 'max': second_heal_max, 'avg': second_heal_avg},
        'third_jump': {'min': third_heal_min, 'max': third_heal_max, 'avg': third_heal_avg}
    }

def calculate_healing_per_second(spell_data, total_healing_power, mp5, total_mana, fight_length):
    """Calculate healing per second accounting for mana constraints and regeneration"""
    # Get spell data
    cast_time = spell_data['cast_time']
    mana_cost = spell_data['mana_cost']
    spell_type = spell_data['name']
    heal_data = calculate_chain_heal_healing(total_healing_power, spell_type)
    
    # Extract healing values
    min_heal = heal_data['total_min']
    max_heal = heal_data['total_max']
    avg_heal = heal_data['total_avg']
    
    # Calculate theoretical HPS (without mana constraints)
    theoretical_min_hps = min_heal / cast_time
    theoretical_max_hps = max_heal / cast_time
    
    # Calculate actual HPS with mana constraints
    current_mana = total_mana
    total_healing_done = 0
    total_casts = 0
    time_elapsed = 0
    last_mp5_tick = 0
    
    # Simulate the fight
    while time_elapsed < fight_length:
        # Check if we can cast the spell
        if current_mana >= mana_cost:
            # Cast the spell
            current_mana -= mana_cost
            total_healing_done += min_heal
            total_casts += 1
            time_elapsed += cast_time
            
            # Check for MP5 regeneration during cast time
            mp5_ticks_during_cast = int((time_elapsed - last_mp5_tick) / 5)
            if mp5_ticks_during_cast > 0:
                current_mana += mp5_ticks_during_cast * mp5
                last_mp5_tick += mp5_ticks_during_cast * 5
        else:
            # Not enough mana, wait for MP5 tick
            time_to_next_mp5 = 5 - ((time_elapsed - last_mp5_tick) % 5)
            if time_to_next_mp5 == 0:
                time_to_next_mp5 = 5
            
            # Skip to next MP5 tick
            time_elapsed += time_to_next_mp5
            current_mana += mp5
            last_mp5_tick = time_elapsed
            
            # If we still can't cast after MP5 tick, we're out of options
            if current_mana < mana_cost and time_elapsed >= fight_length:
                break
    
    # Calculate actual HPS
    actual_min_hps = total_healing_done / fight_length if fight_length > 0 else 0
    
    # For max HPS, assume all heals are maximum values
    actual_max_hps = (total_casts * max_heal) / fight_length if fight_length > 0 else 0
    
    return {
        'theoretical_min_hps': theoretical_min_hps,
        'theoretical_max_hps': theoretical_max_hps,
        'actual_min_hps': actual_min_hps,
        'actual_max_hps': actual_max_hps,
        'total_casts': total_casts,
        'total_healing': total_healing_done,
        'min_heal_per_cast': min_heal,
        'max_heal_per_cast': max_heal,
        'mana_efficiency': total_healing_done / (total_casts * mana_cost) if total_casts > 0 else 0,
        'heal_breakdown': heal_data
    }

def main():
    # Display title with shaman icon
    col1, col2 = st.columns([1, 4])
    with col1:
        st.image("shaman_icon.jpg", width=80)
    with col2:
        st.markdown("# ⚡ Shaman Chain Healing Calculator")
        st.markdown("Calculate healing per second with mana management for your shaman character")
    
    # Spell data dictionary (expandable for future spells)
    spells = {
        "Chain Heal w/ T2 bonus": {
            "name": "Chain Heal",
            "cast_time": 2.5,
            "mana_cost": 340,  # Typical Chain Heal mana cost
            "description": "Base healing: 567-646, +55.36% healing power scaling. 3 jumps, -20% per jump (T2 bonus)"
        },
        "Chain Heal w/o T2 bonus": {
            "name": "Chain Heal w/o T2 bonus",
            "cast_time": 2.5,
            "mana_cost": 340,  # Same mana cost
            "description": "Base healing: 567-646, +55.36% healing power scaling. 3 jumps, -50% per jump (no T2 bonus)"
        },
        "Chain Heal w/ T2.5 + T2 bonus": {
            "name": "Chain Heal",
            "cast_time": 2.1,
            "mana_cost": 340,  # Same mana cost
            "description": "Base healing: 567-646, +55.36% healing power scaling. 3 jumps, -20% per jump (T2 bonus), 2.1s cast (T2.5 bonus)"
        },
        "Chain Heal w/ T2.5 w/o T2 bonus": {
            "name": "Chain Heal w/o T2 bonus",
            "cast_time": 2.1,
            "mana_cost": 340,  # Same mana cost
            "description": "Base healing: 567-646, +55.36% healing power scaling. 3 jumps, -50% per jump (no T2 bonus), 2.1s cast (T2.5 bonus)"
        }
    }
    
    # Create input form
    with st.form("healing_calculator"):
        st.subheader("⚔️ Spell Selection")
        selected_spell = st.selectbox(
            "Choose your spell:",
            list(spells.keys()),
            help="Select the healing spell to calculate"
        )
        
        st.markdown(f"**{selected_spell}:** {spells[selected_spell]['description']}")
        
        st.subheader("📊 Character Stats")
        col1, col2 = st.columns(2)
        
        with col1:
            total_healing_power = st.number_input(
                "Total +Healing Power",
                min_value=0,
                max_value=5000,
                value=0,
                help="Your total +healing power from gear and buffs"
            )
            
            total_mana = st.number_input(
                "Total Mana Pool",
                min_value=100,
                max_value=20000,
                value=5000,
                help="Your character's total mana pool"
            )
        
        with col2:
            mp5 = st.number_input(
                "MP5 (Mana per 5 seconds)",
                min_value=0,
                max_value=1000,
                value=50,
                help="Mana regeneration per 5 seconds"
            )
            
            fight_length = st.number_input(
                "Fight Length (seconds)",
                min_value=1,
                max_value=3600,
                value=300,
                help="Duration of the fight in seconds"
            )
        
        st.subheader("💊 Consumables")
        major_mana_potion = st.selectbox(
            "Major Mana Potion Used?",
            ["No", "Yes"],
            help="Major Mana Potion adds 2000 mana to your total mana pool"
        )
        
        # Calculate effective mana pool
        effective_mana = total_mana
        if major_mana_potion == "Yes":
            effective_mana += 2000
            st.info(f"💊 Major Mana Potion: +2000 mana (Total: {effective_mana:,} mana)")
        
        # Calculate button
        calculate_button = st.form_submit_button("🧮 Calculate Healing", type="primary")
    
    # Perform calculations when button is clicked
    if calculate_button:
        try:
            # Validate inputs
            if fight_length <= 0:
                st.error("Fight length must be greater than 0 seconds")
                return
            
            if effective_mana < spells[selected_spell]['mana_cost']:
                st.error(f"Total mana pool is insufficient to cast {selected_spell} even once!")
                return
            
            # Calculate results
            results = calculate_healing_per_second(
                spells[selected_spell],
                total_healing_power,
                mp5,
                effective_mana,
                fight_length
            )
            
            # Display results
            st.subheader("📈 Calculation Results")
            
            # Main metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Minimum HPS",
                    f"{results['actual_min_hps']:.1f}",
                    help="Minimum healing per second accounting for mana constraints"
                )
            
            with col2:
                st.metric(
                    "Maximum HPS",
                    f"{results['actual_max_hps']:.1f}",
                    help="Maximum potential healing per second"
                )
            
            with col3:
                st.metric(
                    "Total Casts",
                    f"{results['total_casts']:,}",
                    help="Number of spell casts during the fight"
                )
            
            # Additional details
            with st.expander("📋 Detailed Breakdown"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Healing Per Cast:**")
                    st.write(f"• Minimum: {results['min_heal_per_cast']:.1f}")
                    st.write(f"• Maximum: {results['max_heal_per_cast']:.1f}")
                    st.write(f"• Total Healing: {results['total_healing']:,.0f}")
                    if major_mana_potion == "Yes":
                        st.write(f"• Effective Mana: {effective_mana:,} (+2000 from potion)")
                
                with col2:
                    st.write("**Theoretical (No Mana Limit):**")
                    st.write(f"• Minimum HPS: {results['theoretical_min_hps']:.1f}")
                    st.write(f"• Maximum HPS: {results['theoretical_max_hps']:.1f}")
                    st.write(f"• Mana Efficiency: {results['mana_efficiency']:.2f} heal/mana")
                
                # Chain Heal jump breakdown
                if 'heal_breakdown' in results:
                    st.write("**Chain Heal Jump Breakdown:**")
                    breakdown = results['heal_breakdown']
                    st.write(f"• 1st Jump: {breakdown['first_jump']['avg']:.1f} avg ({breakdown['first_jump']['min']:.1f}-{breakdown['first_jump']['max']:.1f})")
                    st.write(f"• 2nd Jump: {breakdown['second_jump']['avg']:.1f} avg ({breakdown['second_jump']['min']:.1f}-{breakdown['second_jump']['max']:.1f})")
                    st.write(f"• 3rd Jump: {breakdown['third_jump']['avg']:.1f} avg ({breakdown['third_jump']['min']:.1f}-{breakdown['third_jump']['max']:.1f})")
                    st.write(f"• **Total per Cast: {breakdown['total_avg']:.1f} avg ({breakdown['total_min']:.1f}-{breakdown['total_max']:.1f})**")
            
            # Performance analysis
            if results['actual_min_hps'] < results['theoretical_min_hps']:
                efficiency = (results['actual_min_hps'] / results['theoretical_min_hps']) * 100
                st.warning(f"⚠️ Mana limited! You're achieving {efficiency:.1f}% of theoretical HPS. Consider increasing MP5 or mana pool.")
            else:
                st.success("✅ Mana sufficient! You can maintain optimal healing throughout the fight.")
            
        except Exception as e:
            st.error(f"An error occurred during calculation: {str(e)}")
            st.error("Please check your inputs and try again.")
    
    # Additional information
    with st.expander("ℹ️ How This Works"):
        st.markdown("""
        **Calculation Method:**
        
        1. **Base Healing:** Chain Heal heals for 567-646 base damage on first target
        2. **Healing Power Scaling:** Adds 55.36% of your +healing power to each jump
        3. **Chain Heal Jumps:** Heals 3 targets total (initial + 2 jumps)
        4. **Jump Reduction:** 
           - With T2 bonus: Each jump loses 20% healing (80% effectiveness)
           - Without T2 bonus: Each jump loses 50% healing (50% effectiveness)
        5. **Cast Time:** 
           - Standard: 2.5 seconds per cast
           - With T2.5 bonus: 2.1 seconds per cast (faster casting)
        6. **Mana Management:** Tracks mana usage and MP5 regeneration
        7. **Major Mana Potion:** Adds 2000 mana to your total mana pool
        8. **Fight Simulation:** Simulates the entire fight duration
        
        **MP5 Regeneration:** Occurs every 5 seconds during the fight
        
        **Mana Constraints:** If you run out of mana, the calculator waits for MP5 ticks before continuing
        """)

if __name__ == "__main__":
    main()
