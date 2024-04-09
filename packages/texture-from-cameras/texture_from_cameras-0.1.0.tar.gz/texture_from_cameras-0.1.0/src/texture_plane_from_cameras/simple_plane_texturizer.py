import pymeshlab

def save_textured_plane(bundle_out, images_list_txt, plane_ply, output_ply):
    # Load project and mesh, apply filters, and save mesh
    try:
        ms = pymeshlab.MeshSet()
        ms.load_project([bundle_out, images_list_txt])
        ms.load_new_mesh(plane_ply)
        ms.apply_filter("set_camera_per_raster")
        ms.apply_filter("compute_texcoord_parametrization_and_texture_from_registered_rasters")
        ms.save_current_mesh(output_ply)
    except Exception as e:
        print(f"An error occurred: {e}")
