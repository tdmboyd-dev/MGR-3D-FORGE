import unittest

from forge.hardware import ComputeProfile, ModelRequirement, assess_local_model


class HardwareGateTests(unittest.TestCase):
    def setUp(self):
        self.laptop=ComputeProfile(15.7,2.0,"Intel Iris Xe",False,True)

    def test_local_cpu_path_allowed(self):
        job=ModelRequirement("native CPU geometry",2,0,False,True,True)
        self.assertTrue(assess_local_model(self.laptop,job)["local_admitted"])

    def test_cuda_heavy_model_rejected(self):
        job=ModelRequirement("large neural texture worker",12,21,True,False,True)
        result=assess_local_model(self.laptop,job)
        self.assertFalse(result["local_admitted"])
        self.assertIn("CUDA GPU runtime unavailable",result["blockers"])

    def test_unverified_license_stops_even_cpu(self):
        job=ModelRequirement("uncleared model",2,0,False,True,False)
        self.assertFalse(assess_local_model(self.laptop,job)["local_admitted"])

    def test_shared_gpu_memory_not_treated_as_dedicated(self):
        job=ModelRequirement("GPU memory dependent model",2,1,False,False,True)
        self.assertIn("verified dedicated GPU memory unavailable",
                      assess_local_model(self.laptop,job)["blockers"])


if __name__=="__main__":
    unittest.main()
