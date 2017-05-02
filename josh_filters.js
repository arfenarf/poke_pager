// The thresholds are 20 for Okay, 40 for Good, 60 for Great, and 80 for Best.
function getValue($pokemon) {
    global
    $cpMap;
    $value = 1;
    $move1 = $pokemon['move_1'];
    $move2 = $pokemon['move_2'];
    $level = $cpMap[$pokemon['encounter_id']] ? $cpMap[$pokemon['encounter_id']]['level'] : 0;

    $iv = ($pokemon['iv_a'] + $pokemon['iv_d'] + $pokemon['iv_s']) / 0.45;
    switch ($pokemon['name']) {
        case 'Snorlax':
            $value = 80 + ($iv / 3);
            if ($move2 == 'Earthquake')
                $value -= 20;
            if ($level && $level < 25)
                $value -= 25 - $level;
            break;

        case 'Lapras':
            $value = 60 + ($iv / 3);
            if ($move2 == 'Water Gun')
                $value -= 10;
            if ($move2 == 'Blizzard')
                $value += 10;
            break;

        case 'Dragonite':
            $value = 70 + ($iv / 3);
            if ($move1 == 'Dragon Tail' && $move2 == 'Outrage')
                $value += 10;
            else if ($move1 == 'Dragon Tail')
                $value += 5;
            break;

        case 'Dratini':
        case 'Dragonair':
            $value = ($iv >= 82) ? $iv : 50 + ($iv / 10);
            break;

        case 'Chansey':
            $value = 50 + $iv / 2;
            break;

        case 'Tangela':
            $value = 50 + $iv / 3;
            if ($move2 == 'Solar Beam')
                $value += 10;
            if ($move2 == 'Sludge Bomb')
                $value -= 10;
            break;

        case 'Aerodactyl':
            $value = 70 + $iv / 6;
            break;

        case 'Vaporeon':
            $value = 70 + $iv / 3;
            if ($move2 == "Hydro Pump")
                $value += 10;
            else if ($level && $level > 20)
                $value += ($level - 20) * 2; // For defensive movesets, add up to 20 points
            break;

        case 'Jolteon':
            $value = 50 + $iv / 3;
            if ($move2 == 'Discharge')
                $value -= 20;
            break;

        case 'Omastar':
            $value = 60 + $iv / 3;
            if ($move1 == 'Water Gun' && $move2 == 'Hydro Pump')
                $value += 20;
            break;

        case 'Exeggutor':
            $value = 50 + ($iv / 4);
            break;

        case 'Alakazam':
            $value = 40 + ($iv / 4);
            if ($move1 == 'Psycho Cut')
                $value += 20;
            if ($move2 == 'Psychic')
                $value += 5;
            break;

        case 'Slowbro':
            $value = ($iv / 2);
            if ($move1 == 'Water Gun')
                $value += 10;
            if ($move2 == 'Psychic')
                $value += 5;
            break;


        case 'Rhydon':
            $value = 50 + ($iv / 4);
            if ($move2 == 'Megahorn')
                $value -= 10;
            break;

        case 'Venusaur':
            $value = 50 + ($iv / 4);
            if ($move1 == 'Vine Whip' && $move2 == 'Solar Beam')
                $value += 20;
            if ($move1 == 'Vine Whip' && $move2 == 'Petal Blizzard')
                $value += 10;
            break;


        case 'Gyarados':
            $value = 60 + $iv / 3;
            if ($move2 == 'Twister')
                $value -= 20;
            break;

        case 'Charizard':
            $value = 40 + $iv / 4;
            if ($move1 == 'Wing Attack')
                $value += 10;
            if ($move2 == 'Dragon Claw')
                $value -= 10;
            break;

        case 'Blastoise':
        case 'Golduck':
        case 'Starmie':
        case 'Seadra':
            $value = ($pokemon['name'] == 'Blastoise' ? 30 : 20) + $iv / 4;
            if ($move1 == 'Water Gun' && $move2 == 'Hydro Pump')
                $value += 10;
            break;

        case 'Poliwrath':
            $value = 30 + ($iv / 4);
            break;

        case 'Arcanine':
            $value = 40 + ($iv / 4);
            if ($move2 == 'Fire Blast')
                $value += 10;
            if ($move2 == 'Bulldozer')
                $value -= 10;
            break;

        case 'Golem':
            $value = 40 + ($iv / 4);
            if ($move1 == 'Mud Slap')
                $value += 10;
            break;

        case 'Lickitung':
            $value = 10 + ($iv / 8);
            break;

        case 'Machamp':
            $value = 50 + ($iv / 4);
            if ($move1 == 'Karate Chop' && $move2 == 'Cross Chop')
                $value += 10;
            break;

        case 'Clefable':
        case 'Wigglytuff':
            $value = $iv / 4;
            if ($move1 == 'Pound' && $move2 == 'Hyper Beam')
                $value += 20;
            if ($move1 == 'Pound' && $move2 == 'Moonblast')
                $value += 5;
            break;

        case 'Tentacruel':
            $value = $iv / 4;
            if ($move1 == 'Poison Jab' && $move2 == 'Hydro Pump')
                $value += 10;
            break;

        case 'Magmar':
        case 'Pinsir':
            $value = $iv / 4;
            if ($move1 == 'Fury Cutter' && $move2 == 'X-Scissor')
                $value += 20;
            break;


        case 'Muk':
            $value = 40 + $iv / 4;
            if ($move1 == 'Poison Jab')
                $value += 10;
            if ($move2 == 'Dark Pulse')
                $value -= 10;
            break;

        case 'Cloyster':
        case 'Dewgong':
            $value = ($pokemon['name'] == 'Dewgong' ? 20 : 30) + $iv / 4;
            if ($move1 == 'Frost Breath')
                $value += 15;
            if ($move2 == 'Blizzard')
                $value += 15;
            break;

        case 'Gengar':
            $value = 20 + $iv / 4;
            if ($move1 == 'Shadow Claw' && $move2 == 'Sludge Bomb')
                $value += 10;
            break;

        case 'Pidgeot':
            $value = $iv / 4;
            if ($move1 == 'Wing Attack' && $move2 == 'Hurricane')
                $value += 20;
            break;

        case 'Koffing':
            $value = 10 + $iv / 4;
            break;

        case 'Weezing':
            $value = 60 + $iv / 10;
            break;

        case 'Venomoth':
            $value = 0 + $iv / 10;
            if ($move1 == 'Bug Bite' && $move2 == 'Bug Buzz')
                $value += 10;
            break;

        case 'Scyther':
            $value = 20 + $iv / 4;
            if ($move1 == 'Steel Wing')
                $value -= 10;
            if ($move2 == 'Night Slash')
                $value -= 20;
            break;

        case 'Nidoking':
        case 'Nidoqueen':
        case 'Vileplume':
        case 'Victreebel':
        case 'Hypno':
        case 'Flareon':
        case 'Electabuzz':
        case 'Raichu':
            $value = ($iv > 80) ? 10 + $iv / 4 : $iv / 8;
            break;

        // Pokedex fillers, IVs don't matter much
        case 'Magneton':
        case 'Ninetails':
        case 'Rapidash':
        case 'Sandslash':
        case 'Kabutops':
        case 'Primeape':
        case 'Dodrio':
        case 'Persian':
            $value = 20 + $iv / 6;
            break;

        // Super-rare Pokedex fillers
        case 'Porygon': // Event: remove
            $value = 20 + $iv / 2;
            break;
        case 'Hitmonlee':
        case 'Hitmonchan':
            $value = 90 + $iv / 10;
            break;

        case 'Jigglypuff':
            $value = ($iv >= 90) ? $iv / 2 : $iv / 10;
            break;

        case 'Rhyhorn':
            $value = ($iv >= 90) ? $iv / 1.5 : $iv / 10;
            break;


        // Evolvers, IVs matter tons
        case 'Bulbasaur':
        case 'Ivysaur':
        case 'Charmander':
        case 'Charmeleon':
        case 'Squirtle':
        case 'Wartortle':
        case 'Pikachu':
        case 'Growlithe':
        case 'Slowpoke':
        case 'Abra':
        case 'Kadabra':
        case 'Grimer':
        case 'Exeggcute':
        case 'Machop':
        case 'Shellder':
        case 'Magikarp':
            $value = ($iv >= 92) ? $iv / 1.5 : $iv / 8;
            if ($level && $level < 10)
                $value -= 50;
            else if ($level && $level < 20)
                $value -= 40;
            else if ($level && $level < 25)
                $value -= 10;
            break;

        case 'Eevee':
            $value = ($iv >= 93) ? $iv / 1.5 : $iv / 5.5;
            if ($level && $level < 25)
                $value -= (25 - $level) * 10;
            break;

        case 'Chikorita':
        case 'Cyndaquil':
        case 'Tododile':
        case 'Bayleef':
        case 'Quilava':
        case 'Croconaw':
            $value = 20 + ($iv >= 91) ? $iv / 1.5 : $iv / 4;
            break;

        case 'Meganium':
        case 'Tyhplosion':
        case 'Feraligatr':
            $value = 40 + ($iv >= 91) ? $iv / 1.5 : $iv / 4;
            break;

        case 'Togetic':
            $value = 40 + ($iv / 4);
            break;

        case 'Sudowoodo':
        case 'Phanpy':
        case 'Teddiursa':
            $value = $iv >= 91 ? 20 + ($iv / 4) : $iv / 4;
            break;

        case 'Granbull':
        case 'Qwilfish':
        case 'Scizor':
        case 'Stantler':
            $value = 20 + ($iv >= 91 ? $iv / 1.5 : $iv / 4);
            if ($pokemon['name'] == 'Qwilfish' && date("Ymd") < '20170330')
                $value -= 20; // Event
            break;

        case 'Mareep':
        case 'Flaffy':
            $value = 40 + ($iv >= 82 ? $iv / 1.5 : $iv / 2);
            break;

        case 'Bellossom':
        case 'Politoed':
        case 'Miltank':
        case "Forretress":
        case "Steelix":
        case "Porygon2":
            $value = 40 + ($iv >= 91 ? $iv / 1.5 : $iv / 4);
            break;


        case 'Umbreon':
        case 'Espeon':
        case 'Donphan':
        case 'Ampharos':
        case 'Houndoom':
            $value = 40 + ($iv >= 91 ? $iv / 1.5 : $iv / 4);
            break;

        case 'Larvitar':
        case 'Pupitar':
            $value = 60 + ($iv / 2);
            break;

        case 'Tyranitar':
        case 'Unown':
            $value = 80 + ($iv / 3);
            break;

        case 'Blissey':
        case 'Raikou':
        case 'Heracross':
        case 'Entei':
        case 'Suicune':
        case 'Lugia':
        case 'Ho-Oh':
        case 'Celebi':
            $value = 100;
            break;
    }

    // Bonus points for exceptional IVs:
    if ($iv == 100)
        $value += 60;
    else if ($iv >= 98)
        $value += 30;
    else if ($iv >= 95)
        $value += 20;
    else if ($iv >= 90)
        $value += 10;
    else if ($iv >= 82)
        $value += 5;

    if ($level >= 28)
        $value += 20;
    else if ($level >= 25)
        $value += 10;
    else if ($level >= 20)
        $value += 5;
    else if ($level && $level < 5)
        $value -= 20;
    else if ($level && $level < 15)
        $value -= 10;

    $value = min($value, 100);

    return $value;
}