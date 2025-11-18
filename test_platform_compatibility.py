"""
Test suite for cross-platform compatibility
"""
import unittest
import cv2
import platform
from platform_utils import (
    get_camera_backend,
    initialize_camera,
    find_instruction_image,
    get_platform_info
)


class TestPlatformUtils(unittest.TestCase):
    """Test platform utility functions"""
    
    def test_get_camera_backend(self):
        """Test that camera backend is appropriate for platform"""
        backend = get_camera_backend()
        system = platform.system()
        
        if system == "Darwin":
            self.assertEqual(backend, cv2.CAP_AVFOUNDATION)
        elif system == "Windows":
            self.assertEqual(backend, cv2.CAP_DSHOW)
        elif system == "Linux":
            self.assertEqual(backend, cv2.CAP_V4L2)
        else:
            self.assertEqual(backend, cv2.CAP_ANY)
    
    def test_get_platform_info(self):
        """Test platform info retrieval"""
        info = get_platform_info()
        
        self.assertIn("system", info)
        self.assertIn("python_version", info)
        self.assertIsInstance(info["system"], str)
        self.assertTrue(len(info["system"]) > 0)
    
    def test_find_instruction_image(self):
        """Test instruction image finding (may return None)"""
        path = find_instruction_image()
        # Path can be None if image doesn't exist
        self.assertTrue(path is None or isinstance(path, str))


class TestCameraInitialization(unittest.TestCase):
    """Test camera initialization"""
    
    def test_initialize_camera_returns_tuple(self):
        """Test that camera initialization returns expected tuple"""
        try:
            result = initialize_camera(camera_index=0, target_fps=30)
            self.assertIsInstance(result, tuple)
            self.assertEqual(len(result), 5)
            
            cam, fps, width, height, backend_name = result
            
            # Verify types
            self.assertIsNotNone(cam)
            self.assertIsInstance(fps, (int, float))
            self.assertIsInstance(width, int)
            self.assertIsInstance(height, int)
            self.assertIsInstance(backend_name, str)
            
            # Cleanup
            cam.release()
            
        except RuntimeError as e:
            # Camera may not be available in CI/CD environment
            self.skipTest(f"Camera not available: {e}")


if __name__ == "__main__":
    # Run tests with verbose output
    unittest.main(verbosity=2)
