"""Explicit anatomy must survive mutation and fail before journal allocation."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from forge.anatomy_constraints import parse_anatomy_constraints
from forge.imagination import genome_candidates, creature_meshes, create_original_creature
from forge.creature_rig_recipe import creature_bones
from forge.cli import build
from forge.spec import WorldSpec
from forge.studio_server import ForgeWorkstation


class AnatomyConstraintsTests(unittest.TestCase):
    def test_existing_positive_brief_keeps_its_original_seeded_anatomy(self):
        # Real pre-change baseline f6914ae: adding explicit constraints must not
        # consume extra random draws for an already satisfied 'horned' brief.
        genome = genome_candidates('Invent a horned winged forest creature with a long tail', 21, 1)[0]
        self.assertEqual({key: genome[key] for key in ('body_length', 'body_width', 'body_height',
                         'standing_height', 'tail_length', 'horn_count')},
                         {'body_length': 2.272, 'body_width': .312, 'body_height': .787,
                          'standing_height': 1.425, 'tail_length': 2.522, 'horn_count': 6})

    def test_negated_species_traits_survive_every_variant(self):
        for seed in (0, 19, 42, 4294967295):
            for g in genome_candidates('a dragon without wings or horns, tailless and unarmored', seed, 12):
                self.assertEqual(g['wing_pairs'], 0)
                self.assertEqual(g['horn_count'], 0)
                self.assertEqual(g['tail_length'], 0)
                self.assertEqual(g['armor_ridges'], 0)
                self.assertNotIn('winged', g['meaning_tags'])
                self.assertFalse(creature_meshes(g)[4].indices)
                self.assertFalse(any(b['role'] == 'tail' for b in creature_bones(g)['skeleton']))

    def test_eye_number_never_turns_into_leg_number(self):
        for g in genome_candidates('a four-legged creature with eight eyes and two horns', 17, 12):
            self.assertEqual(g['legs'], 4)
            self.assertEqual(g['eye_count'], 8)
            self.assertEqual(g['horn_count'], 2)
            self.assertNotIn('spider', g['meaning_tags'])
        self.assertEqual(genome_candidates('a gentle creature with two eyes', 8, 1)[0]['legs'], 4)

    def test_supported_eye_counts_emit_exact_number_of_eye_surfaces(self):
        # Every eye uses the original 12x8 ellipsoid, with 168 triangles.
        for count in range(9):
            g = genome_candidates(f'a creature with {count} eyes', 19, 1)[0]
            self.assertEqual(len(creature_meshes(g)[3].indices) // 3, count * 168)

    def test_unsupported_and_conflicting_explicit_anatomy_refuses(self):
        for prompt in ('a creature with six legs', 'a creature with twelve eyes',
                       'a creature with eleven eyes', 'a creature with thirteen legs',
                       'a creature with twenty-one eyes', 'a creature with a dozen legs',
                       'a creature with -4 legs', 'a creature with 3.2 eyes',
                       'a creature with +2 horns', 'a creature with 1/2 eyes',
                       'a creature with 1e2 legs', 'a creature with 1,000 eyes',
                       'a winged creature with no wings', 'a horned creature without horns',
                       'a wingless creature with wings', 'a hornless creature with horns',
                       'a tailless creature with a long tail',
                       'a creature with two horns and four horns', 'an armored unarmored creature'):
            with self.subTest(prompt=prompt), self.assertRaises(ValueError):
                genome_candidates(prompt, 4, 2)

    def test_explicit_zero_wings_is_not_misread_as_positive_presence(self):
        self.assertEqual(parse_anatomy_constraints('a creature with zero wings')['wing_pairs'], 0)
        self.assertEqual(parse_anatomy_constraints('a creature with two wings')['wing_pairs'], 1)

    def test_positive_armor_constraint_survives_all_supported_spellings(self):
        for word in ('armored', 'armoured', 'armor', 'armour'):
            for g in genome_candidates(f'an original creature with {word} and two eyes', 17, 12):
                self.assertGreater(g['armor_ridges'], 0)

    def test_negation_ends_before_new_positive_clause(self):
        constraints = parse_anatomy_constraints('a creature without wings and with two horns')
        self.assertEqual(constraints['wing_pairs'], 0)
        self.assertEqual(constraints['horn_count'], 2)
        self.assertEqual(parse_anatomy_constraints('a wingless hornless creature')['horn_count'], 0)

    def test_bad_brief_refuses_before_any_persistent_job(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            build(WorldSpec(seed=9, columns=2, rows=2, buildings=2), root / 'world')
            studio = ForgeWorkstation(root / 'world', root / 'workspace')
            with self.assertRaisesRegex(ValueError, 'unsupported'):
                studio.command('/api/creature-create', {'request_id': 'bad-anatomy-0001',
                    'prompt': 'an original creature with six legs', 'seed': 0, 'variants': 1, 'morph': {}})
            self.assertFalse(list(studio.jobs.iterdir()))
            self.assertFalse((studio.workspace / 'creature-requests.json').exists())
