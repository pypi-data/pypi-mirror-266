import argparse
import pymeshlab

class PlaneTexturizer:
    def __init__(self):
        self.ms = pymeshlab.MeshSet()

    def load_project(self, file_paths):
        try:
            self.ms.load_project(file_paths)
        except Exception as e:
            print(f"Error loading project: {e}")

    def load_plane(self, file_path):
        try:
            self.ms.load_new_mesh(file_path)
        except Exception as e:
            print(f"Error loading new mesh: {e}")

    def apply_filter(self, filter_name):
        try:
            self.ms.apply_filter(filter_name)
        except Exception as e:
            print(f"Error applying filter '{filter_name}': {e}")

    def save_current_mesh(self, file_path):
        try:
            self.ms.save_current_mesh(file_path)
        except Exception as e:
            print(f"Error saving current mesh: {e}")

    def get_textured_plane(self, bundle_out, images_list_txt, plane_ply, output_ply):
        # Load project and mesh, apply filters, and save mesh
        try:
            self.load_project([bundle_out, images_list_txt])
            self.load_plane(plane_ply)
            self.apply_filter("set_camera_per_raster")
            self.apply_filter("compute_texcoord_parametrization_and_texture_from_registered_rasters")
            self.save_current_mesh(output_ply)
        except Exception as e:
            print(f"An error occurred: {e}")

def parse_arguments():
    parser = argparse.ArgumentParser(description="Process mesh and image files.")
    parser.add_argument("bundle_out", type=str, help="Path to the bundle.out file")
    parser.add_argument("images_list", type=str, help="Path to the images_list.txt file")
    parser.add_argument("plane_ply", type=str, help="Path to the plane.ply file")
    parser.add_argument("output_ply", type=str, help="Path to the output.ply file")

    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    processor = PlaneTexturizer()
    processor.get_textured_plane(args.bundle_out, args.images_list, args.plane_ply, args.output_ply)
