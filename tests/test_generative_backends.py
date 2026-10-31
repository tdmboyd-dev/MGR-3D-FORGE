import unittest
from forge.generative_backends import load_engine_profiles,preflight_generation


class GenerativeBackendsTests(unittest.TestCase):
    def test_researched_riggers_and_hosted_api_are_not_installed_generators(self):
        profiles={p["id"]:p for p in load_engine_profiles()}
        for candidate in ("anigen","unirig","meshanything-v2","riganything-research",
                          "higgsfield-3d-service","hunyuan3d-omni","sam-3d-objects"):
            with self.subTest(candidate=candidate):
                self.assertFalse(profiles[candidate]["runtime_ready"])
                state=preflight_generation(candidate,gpu_vram_gb=80,weights_available=True,
                                           rights_approved=True,budget_usd=200)
                self.assertFalse(state["can_run_now"])
                self.assertTrue(state["blockers"])
        self.assertIn("RESTRICTED",profiles["anigen"]["license_status"])
        self.assertIn("NONCOMMERCIAL",profiles["riganything-research"]["license_status"])
        self.assertIn("PROPRIETARY",profiles["higgsfield-3d-service"]["license_status"])

    def test_native_only_currently_executable_without_external_weights(self):
        profiles=load_engine_profiles()
        self.assertGreaterEqual(len(profiles),6)
        self.assertEqual(len({p["id"] for p in profiles}),len(profiles))
        ready=preflight_generation("mgr-native-imagination")
        self.assertTrue(ready["can_run_now"])
        self.assertFalse(ready["model_inference_performed"])
        self.assertFalse(ready["hosted_api_usage"])

    def test_external_weights_are_not_implicitly_installed_or_unlimited(self):
        for name in ("trellis-2","pixal3d","triposr","hunyuan3d-2.1","trellis-original"):
            with self.subTest(engine=name):
                result=preflight_generation(name,gpu_vram_gb=48,
                    budget_usd=5,weights_available=True,rights_approved=True)
                self.assertFalse(result["can_run_now"])
                self.assertEqual(result["status"],"ADAPTER_NOT_INSTALLED")
                self.assertTrue(any("not installed" in x for x in result["blockers"]))

    def test_unlicensed_gpu_job_cannot_be_promoted(self):
        r=preflight_generation("hunyuan3d-2.1",gpu_vram_gb=80,budget_usd=100,
                               weights_available=True,rights_approved=False)
        self.assertFalse(r["can_run_now"])
        self.assertTrue(any("license" in x for x in r["blockers"]))
        self.assertFalse(r["hosted_api_usage"])

    def test_invalid_requests_fail(self):
        for kwargs in ({"budget_usd":-1},{"gpu_vram_gb":float("nan")},
                       {"weights_available":"yes"},{"rights_approved":"yes"}):
            with self.subTest(kwargs=kwargs),self.assertRaises(ValueError):
                preflight_generation("trellis-2",**kwargs)
        with self.assertRaises(ValueError): preflight_generation("nonexistent")
