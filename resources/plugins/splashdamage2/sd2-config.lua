-------------------------------------------------------------------------------------------------------------------------------------------------------------
-- configuration file for Splash Damage 2 Plugin
--
-- This configuration is tailored for a mission generated by DCS Retribution
-- see https://github.com/dcs-retribution/dcs-retribution
-------------------------------------------------------------------------------------------------------------------------------------------------------------


-- SD2 plugin - configuration
if dcsRetribution then
    -- retrieve specific options values
    if dcsRetribution.plugins then
        if dcsRetribution.plugins.splashdamage2 then
            env.info("DCSRetribution|Splash Damage 2 plugin - Setting Up")

            splash_damage_options.wave_explosions = dcsRetribution.plugins.splashdamage2.wave_explosions
            splash_damage_options.damage_model = dcsRetribution.plugins.splashdamage2.damage_model
            splash_damage_options.debug = dcsRetribution.plugins.splashdamage2.debug
            splash_damage_options.explTable_multiplier = dcsRetribution.plugins.splashdamage2.explTable_multiplier
            splash_damage_options.static_damage_boost = dcsRetribution.plugins.splashdamage2.static_damage_boost
            splash_damage_options.blast_search_radius = dcsRetribution.plugins.splashdamage2.blast_search_radius
        end
    end
end
