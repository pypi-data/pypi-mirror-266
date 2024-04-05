from typing import List, Optional, Dict, Iterable
import io
import aspose.pycore
import aspose.pydrawing
import aspose.cad
import aspose.cad.annotations
import aspose.cad.cadexceptions
import aspose.cad.cadexceptions.compressors
import aspose.cad.cadexceptions.imageformats
import aspose.cad.exif
import aspose.cad.exif.enums
import aspose.cad.fileformats
import aspose.cad.fileformats.bmp
import aspose.cad.fileformats.cad
import aspose.cad.fileformats.cad.cadconsts
import aspose.cad.fileformats.cad.cadobjects
import aspose.cad.fileformats.cad.cadobjects.acadtable
import aspose.cad.fileformats.cad.cadobjects.attentities
import aspose.cad.fileformats.cad.cadobjects.background
import aspose.cad.fileformats.cad.cadobjects.blocks
import aspose.cad.fileformats.cad.cadobjects.datatable
import aspose.cad.fileformats.cad.cadobjects.dictionary
import aspose.cad.fileformats.cad.cadobjects.dimassoc
import aspose.cad.fileformats.cad.cadobjects.field
import aspose.cad.fileformats.cad.cadobjects.hatch
import aspose.cad.fileformats.cad.cadobjects.helpers
import aspose.cad.fileformats.cad.cadobjects.mlinestyleobject
import aspose.cad.fileformats.cad.cadobjects.objectcontextdataclasses
import aspose.cad.fileformats.cad.cadobjects.perssubentmanager
import aspose.cad.fileformats.cad.cadobjects.polylines
import aspose.cad.fileformats.cad.cadobjects.section
import aspose.cad.fileformats.cad.cadobjects.sunstudy
import aspose.cad.fileformats.cad.cadobjects.tablestyle
import aspose.cad.fileformats.cad.cadobjects.underlaydefinition
import aspose.cad.fileformats.cad.cadobjects.vertices
import aspose.cad.fileformats.cad.cadobjects.wipeout
import aspose.cad.fileformats.cad.cadparameters
import aspose.cad.fileformats.cad.cadtables
import aspose.cad.fileformats.cad.dwg
import aspose.cad.fileformats.cad.dwg.acdbobjects
import aspose.cad.fileformats.cad.dwg.appinfo
import aspose.cad.fileformats.cad.dwg.pageandsection
import aspose.cad.fileformats.cad.dwg.pageandsection.writer
import aspose.cad.fileformats.cad.dwg.r2004
import aspose.cad.fileformats.cad.dwg.revhistory
import aspose.cad.fileformats.cad.dwg.summaryinfo
import aspose.cad.fileformats.cad.dwg.vbaproject
import aspose.cad.fileformats.cad.geometry
import aspose.cad.fileformats.cad.watermarkguard
import aspose.cad.fileformats.cf2
import aspose.cad.fileformats.cgm
import aspose.cad.fileformats.cgm.classes
import aspose.cad.fileformats.cgm.commands
import aspose.cad.fileformats.cgm.elements
import aspose.cad.fileformats.cgm.enums
import aspose.cad.fileformats.cgm.export
import aspose.cad.fileformats.cgm.import
import aspose.cad.fileformats.collada
import aspose.cad.fileformats.collada.fileparser
import aspose.cad.fileformats.collada.fileparser.elements
import aspose.cad.fileformats.dgn
import aspose.cad.fileformats.dgn.dgnelements
import aspose.cad.fileformats.dgn.dgntransform
import aspose.cad.fileformats.dwf
import aspose.cad.fileformats.dwf.dwfxps
import aspose.cad.fileformats.dwf.dwfxps.fixedpage
import aspose.cad.fileformats.dwf.dwfxps.fixedpage.dto
import aspose.cad.fileformats.dwf.whip
import aspose.cad.fileformats.dwf.whip.objects
import aspose.cad.fileformats.dwf.whip.objects.drawable
import aspose.cad.fileformats.dwf.whip.objects.drawable.text
import aspose.cad.fileformats.dwf.whip.objects.service
import aspose.cad.fileformats.dwf.whip.objects.service.font
import aspose.cad.fileformats.dwg
import aspose.cad.fileformats.dwg.pageandsection
import aspose.cad.fileformats.fbx
import aspose.cad.fileformats.glb
import aspose.cad.fileformats.glb.animations
import aspose.cad.fileformats.glb.geometry
import aspose.cad.fileformats.glb.geometry.vertextypes
import aspose.cad.fileformats.glb.io
import aspose.cad.fileformats.glb.materials
import aspose.cad.fileformats.glb.memory
import aspose.cad.fileformats.glb.runtime
import aspose.cad.fileformats.glb.scenes
import aspose.cad.fileformats.glb.toolkit
import aspose.cad.fileformats.glb.transforms
import aspose.cad.fileformats.glb.validation
import aspose.cad.fileformats.ifc
import aspose.cad.fileformats.ifc.header
import aspose.cad.fileformats.ifc.ifc2x3
import aspose.cad.fileformats.ifc.ifc2x3.entities
import aspose.cad.fileformats.ifc.ifc2x3.types
import aspose.cad.fileformats.ifc.ifc4
import aspose.cad.fileformats.ifc.ifc4.entities
import aspose.cad.fileformats.ifc.ifc4.types
import aspose.cad.fileformats.ifc.ifcdrawing
import aspose.cad.fileformats.ifc.ifcdrawing.visitors
import aspose.cad.fileformats.iges
import aspose.cad.fileformats.iges.commondefinitions
import aspose.cad.fileformats.iges.drawables
import aspose.cad.fileformats.jpeg
import aspose.cad.fileformats.jpeg2000
import aspose.cad.fileformats.obj
import aspose.cad.fileformats.obj.elements
import aspose.cad.fileformats.obj.mtl
import aspose.cad.fileformats.obj.vertexdata
import aspose.cad.fileformats.obj.vertexdata.index
import aspose.cad.fileformats.pdf
import aspose.cad.fileformats.plt
import aspose.cad.fileformats.plt.pltparsers
import aspose.cad.fileformats.plt.pltparsers.pltparser
import aspose.cad.fileformats.plt.pltparsers.pltparser.pltcommands
import aspose.cad.fileformats.plt.pltparsers.pltparser.pltplotitems
import aspose.cad.fileformats.png
import aspose.cad.fileformats.psd
import aspose.cad.fileformats.psd.resources
import aspose.cad.fileformats.shx
import aspose.cad.fileformats.stl
import aspose.cad.fileformats.stl.stlobjects
import aspose.cad.fileformats.stp
import aspose.cad.fileformats.stp.helpers
import aspose.cad.fileformats.stp.items
import aspose.cad.fileformats.stp.reader
import aspose.cad.fileformats.stp.stplibrary
import aspose.cad.fileformats.stp.stplibrary.core
import aspose.cad.fileformats.stp.stplibrary.core.models
import aspose.cad.fileformats.svg
import aspose.cad.fileformats.threeds
import aspose.cad.fileformats.threeds.elements
import aspose.cad.fileformats.tiff
import aspose.cad.fileformats.tiff.enums
import aspose.cad.fileformats.tiff.filemanagement
import aspose.cad.fileformats.tiff.instancefactory
import aspose.cad.fileformats.tiff.tifftagtypes
import aspose.cad.fileformats.u3d
import aspose.cad.fileformats.u3d.bitstream
import aspose.cad.fileformats.u3d.elements
import aspose.cad.imagefilters
import aspose.cad.imagefilters.filteroptions
import aspose.cad.imageoptions
import aspose.cad.imageoptions.svgoptionsparameters
import aspose.cad.measurement
import aspose.cad.palettehelper
import aspose.cad.primitives
import aspose.cad.sources
import aspose.cad.timeprovision
import aspose.cad.watermarkguard

class SortedSetUIntDescending:
    
    ...

class U3dAuthorFace:
    '''The face of the author (progressive) mesh.'''
    
    def indexer_get(self, index : int) -> int:
        ...
    
    def indexer_set(self, index : int, value : int) -> None:
        ...
    
    @property
    def a(self) -> int:
        ...
    
    @a.setter
    def a(self, value : int):
        ...
    
    @property
    def b(self) -> int:
        ...
    
    @b.setter
    def b(self, value : int):
        ...
    
    @property
    def c(self) -> int:
        ...
    
    @c.setter
    def c(self, value : int):
        ...
    
    def __getitem__(self, key : int) -> int:
        ...
    
    def __setitem__(self, key : int, value : int):
        ...
    
    ...

class U3dAuthorFaceUpdate:
    '''The structure containing information on how face data is added to or
    removed from a mesh during mesh resolution changes.'''
    
    @property
    def face_index(self) -> int:
        ...
    
    @face_index.setter
    def face_index(self, value : int):
        ...
    
    @property
    def corner(self) -> int:
        ...
    
    @corner.setter
    def corner(self, value : int):
        ...
    
    @property
    def attribute(self) -> U3dAuthorFaceUpdate.AttributeType:
        ...
    
    @attribute.setter
    def attribute(self, value : U3dAuthorFaceUpdate.AttributeType):
        ...
    
    @property
    def incr_value(self) -> int:
        ...
    
    @incr_value.setter
    def incr_value(self, value : int):
        ...
    
    @property
    def decr_value(self) -> int:
        ...
    
    @decr_value.setter
    def decr_value(self, value : int):
        ...
    
    ...

class U3dAuthorLineSet:
    
    def get_line_set_desc(self) -> aspose.cad.fileformats.u3d.elements.U3dAuthorLineSetDescription:
        ...
    
    def get_max_line_set_desc(self) -> aspose.cad.fileformats.u3d.elements.U3dAuthorLineSetDescription:
        ...
    
    def normalize_normals(self) -> None:
        ...
    
    def get_position(self, index : int, p_out_vector3 : Any) -> None:
        ...
    
    def set_position(self, index : int, p_in_vector3 : aspose.cad.Vector3F) -> None:
        ...
    
    def get_normal(self, index : int, p_vector3 : Any) -> None:
        ...
    
    def set_normal(self, index : int, p_vector3 : aspose.cad.Vector3F) -> None:
        ...
    
    def get_diffuse_color(self, index : int, p_color : Any) -> None:
        ...
    
    def set_diffuse_color(self, index : int, p_color : aspose.cad.Vector4F) -> None:
        ...
    
    def get_specular_color(self, index : int, p_color : Any) -> None:
        ...
    
    def set_specular_color(self, index : int, p_color : aspose.cad.Vector4F) -> None:
        ...
    
    def get_tex_coord(self, index : int, p_color : Any) -> None:
        ...
    
    def set_tex_coord(self, index : int, p_color : aspose.cad.Vector4F) -> None:
        ...
    
    def get_position_line(self, index : int, p_position_line : Any) -> None:
        ...
    
    def set_position_line(self, index : int, p_position_line : aspose.cad.fileformats.u3d.elements.U3dLine) -> None:
        ...
    
    def get_normal_line(self, index : int, p_normal_line : Any) -> None:
        ...
    
    def set_normal_line(self, index : int, p_normal_line : aspose.cad.fileformats.u3d.elements.U3dLine) -> None:
        ...
    
    def get_diffuse_line(self, index : int, p_diffuse_line : Any) -> None:
        ...
    
    def set_diffuse_line(self, index : int, p_diffuse_line : aspose.cad.fileformats.u3d.elements.U3dLine) -> None:
        ...
    
    def get_specular_line(self, index : int, p_specular_line : Any) -> None:
        ...
    
    def set_specular_line(self, index : int, p_specular_line : aspose.cad.fileformats.u3d.elements.U3dLine) -> None:
        ...
    
    def get_tex_line(self, layer : int, index : int, p_line : Any) -> None:
        ...
    
    def set_tex_line(self, layer : int, index : int, p_line : aspose.cad.fileformats.u3d.elements.U3dLine) -> None:
        ...
    
    def get_line_material(self, index : int, p_line_material : Any) -> None:
        ...
    
    def set_line_material(self, index : int, line_material_id : int) -> None:
        ...
    
    def get_material(self, index : int, p_material : Any) -> None:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def positions(self) -> List[aspose.cad.Vector3F]:
        ...
    
    @positions.setter
    def positions(self, value : List[aspose.cad.Vector3F]):
        ...
    
    @property
    def position_lines(self) -> List[aspose.cad.fileformats.u3d.elements.U3dLine]:
        ...
    
    @position_lines.setter
    def position_lines(self, value : List[aspose.cad.fileformats.u3d.elements.U3dLine]):
        ...
    
    ...

class U3dAuthorLineSetDescription:
    '''The author (progressive) line set description.'''
    
    def copy(self) -> aspose.cad.fileformats.u3d.elements.U3dAuthorLineSetDescription:
        ...
    
    @property
    def shaders(self) -> List[aspose.cad.fileformats.u3d.elements.U3dAuthorMaterial]:
        ...
    
    @shaders.setter
    def shaders(self, value : List[aspose.cad.fileformats.u3d.elements.U3dAuthorMaterial]):
        ...
    
    @property
    def num_lines(self) -> int:
        ...
    
    @num_lines.setter
    def num_lines(self, value : int):
        ...
    
    @property
    def num_positions(self) -> int:
        ...
    
    @num_positions.setter
    def num_positions(self, value : int):
        ...
    
    @property
    def num_normals(self) -> int:
        ...
    
    @num_normals.setter
    def num_normals(self, value : int):
        ...
    
    @property
    def num_diffuse_colors(self) -> int:
        ...
    
    @num_diffuse_colors.setter
    def num_diffuse_colors(self, value : int):
        ...
    
    @property
    def num_specular_colors(self) -> int:
        ...
    
    @num_specular_colors.setter
    def num_specular_colors(self, value : int):
        ...
    
    @property
    def num_tex_coords(self) -> int:
        ...
    
    @num_tex_coords.setter
    def num_tex_coords(self, value : int):
        ...
    
    @property
    def num_materials(self) -> int:
        ...
    
    @num_materials.setter
    def num_materials(self, value : int):
        ...
    
    ...

class U3dAuthorMaterial:
    
    @property
    def material_attributes(self) -> int:
        ...
    
    @material_attributes.setter
    def material_attributes(self, value : int):
        ...
    
    @property
    def num_texture_layers(self) -> int:
        ...
    
    @num_texture_layers.setter
    def num_texture_layers(self, value : int):
        ...
    
    @property
    def original_shading_id(self) -> int:
        ...
    
    @original_shading_id.setter
    def original_shading_id(self, value : int):
        ...
    
    @property
    def has_diffuse_colors(self) -> bool:
        ...
    
    @has_diffuse_colors.setter
    def has_diffuse_colors(self, value : bool):
        ...
    
    @property
    def has_specular_colors(self) -> bool:
        ...
    
    @has_specular_colors.setter
    def has_specular_colors(self, value : bool):
        ...
    
    @property
    def tex_coord_dimensions(self) -> List[int]:
        ...
    
    @tex_coord_dimensions.setter
    def tex_coord_dimensions(self, value : List[int]):
        ...
    
    @property
    def has_normals(self) -> bool:
        ...
    
    @has_normals.setter
    def has_normals(self, value : bool):
        ...
    
    ...

class U3dAuthorMesh:
    
    def get_mesh_desc(self) -> aspose.cad.fileformats.u3d.elements.U3dAuthorMeshDescription:
        ...
    
    def get_max_mesh_desc(self) -> aspose.cad.fileformats.u3d.elements.U3dAuthorMeshDescription:
        ...
    
    def get_min_resolution(self) -> int:
        ...
    
    def set_resolution(self, r : int) -> int:
        ...
    
    def get_final_max_resolution(self) -> int:
        ...
    
    def set_position_face(self, index : int, p_in_position_face : aspose.cad.fileformats.u3d.elements.U3dAuthorFace) -> None:
        ...
    
    def set_vertex_update(self, index : int, p_in_vertex_update : aspose.cad.fileformats.u3d.elements.U3dAuthorVertexUpdate) -> None:
        ...
    
    def get_position_face(self, index : int, p_out_position_face : Any) -> None:
        ...
    
    def get_position(self, index : int, p_out_vector3 : Any) -> None:
        ...
    
    def set_position(self, index : int, p_in_vector3 : aspose.cad.Vector3F) -> None:
        ...
    
    def set_max_resolution(self, r : int) -> None:
        ...
    
    def get_max_resolution(self) -> int:
        ...
    
    def set_final_max_resolution(self, r : int) -> None:
        ...
    
    def set_min_resolution(self, r : int) -> None:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def position_faces(self) -> List[aspose.cad.fileformats.u3d.elements.U3dAuthorFace]:
        ...
    
    @position_faces.setter
    def position_faces(self, value : List[aspose.cad.fileformats.u3d.elements.U3dAuthorFace]):
        ...
    
    @property
    def positions(self) -> List[aspose.cad.Vector3F]:
        ...
    
    @positions.setter
    def positions(self, value : List[aspose.cad.Vector3F]):
        ...
    
    ...

class U3dAuthorMeshAdjacency:
    
    def add_x(self, u_position_index : int, u_face_index : int) -> None:
        ...
    
    def remove_x(self, u_position_index : int, u_face_index : int) -> None:
        ...
    
    def get_face_set_x(self, u_position_index : int, rp_face_set : Any) -> None:
        ...
    
    def get_position_set_x(self, r_face_set : aspose.cad.fileformats.u3d.elements.SortedSetUIntDescending, rp_position_set : Any) -> None:
        ...
    
    ...

class U3dAuthorMeshDescription:
    '''The author (progressive) mesh description.'''
    
    @property
    def shaders(self) -> List[aspose.cad.fileformats.u3d.elements.U3dAuthorMaterial]:
        ...
    
    @shaders.setter
    def shaders(self, value : List[aspose.cad.fileformats.u3d.elements.U3dAuthorMaterial]):
        ...
    
    @property
    def num_faces(self) -> int:
        ...
    
    @num_faces.setter
    def num_faces(self, value : int):
        ...
    
    @property
    def num_positions(self) -> int:
        ...
    
    @num_positions.setter
    def num_positions(self, value : int):
        ...
    
    @property
    def num_normals(self) -> int:
        ...
    
    @num_normals.setter
    def num_normals(self, value : int):
        ...
    
    @property
    def num_diffuse_colors(self) -> int:
        ...
    
    @num_diffuse_colors.setter
    def num_diffuse_colors(self, value : int):
        ...
    
    @property
    def num_specular_colors(self) -> int:
        ...
    
    @num_specular_colors.setter
    def num_specular_colors(self, value : int):
        ...
    
    @property
    def num_tex_coords(self) -> int:
        ...
    
    @num_tex_coords.setter
    def num_tex_coords(self, value : int):
        ...
    
    @property
    def num_materials(self) -> int:
        ...
    
    @num_materials.setter
    def num_materials(self, value : int):
        ...
    
    @property
    def num_base_vertices(self) -> int:
        ...
    
    @num_base_vertices.setter
    def num_base_vertices(self, value : int):
        ...
    
    ...

class U3dAuthorVertexUpdate:
    '''The structure containing information on how vertex data is added to or
    removed from a mesh during mesh resolution changes.'''
    
    @property
    def num_new_faces(self) -> int:
        ...
    
    @num_new_faces.setter
    def num_new_faces(self, value : int):
        ...
    
    @property
    def num_new_normals(self) -> int:
        ...
    
    @num_new_normals.setter
    def num_new_normals(self, value : int):
        ...
    
    @property
    def num_new_diffuse_colors(self) -> int:
        ...
    
    @num_new_diffuse_colors.setter
    def num_new_diffuse_colors(self, value : int):
        ...
    
    @property
    def num_new_specular_colors(self) -> int:
        ...
    
    @num_new_specular_colors.setter
    def num_new_specular_colors(self, value : int):
        ...
    
    @property
    def num_new_tex_coords(self) -> int:
        ...
    
    @num_new_tex_coords.setter
    def num_new_tex_coords(self, value : int):
        ...
    
    @property
    def num_face_updates(self) -> int:
        ...
    
    @num_face_updates.setter
    def num_face_updates(self, value : int):
        ...
    
    @property
    def face_updates(self) -> List[aspose.cad.fileformats.u3d.elements.U3dAuthorFaceUpdate]:
        ...
    
    @face_updates.setter
    def face_updates(self, value : List[aspose.cad.fileformats.u3d.elements.U3dAuthorFaceUpdate]):
        ...
    
    ...

class U3dBaseMesh:
    
    @property
    def has_positions(self) -> bool:
        ...
    
    @property
    def positions(self) -> List[aspose.cad.Vector3F]:
        ...
    
    @property
    def has_normals(self) -> bool:
        ...
    
    @property
    def normals(self) -> List[aspose.cad.Vector3F]:
        ...
    
    @property
    def has_diffuse_colors(self) -> bool:
        ...
    
    @property
    def diffuse_colors(self) -> List[aspose.cad.Vector4F]:
        ...
    
    @property
    def has_specular_colors(self) -> bool:
        ...
    
    @property
    def specular_colors(self) -> List[aspose.cad.Vector4F]:
        ...
    
    @property
    def tex_coords(self) -> List[aspose.cad.Vector4F]:
        ...
    
    @property
    def faces(self) -> List[aspose.cad.fileformats.u3d.elements.U3dFace]:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    ...

class U3dFace:
    
    @property
    def shading_id(self) -> int:
        ...
    
    @shading_id.setter
    def shading_id(self, value : int):
        ...
    
    @property
    def positions(self) -> aspose.cad.fileformats.u3d.elements.U3dPoly:
        ...
    
    @positions.setter
    def positions(self, value : aspose.cad.fileformats.u3d.elements.U3dPoly):
        ...
    
    @property
    def normals(self) -> aspose.cad.fileformats.u3d.elements.U3dPoly:
        ...
    
    @normals.setter
    def normals(self, value : aspose.cad.fileformats.u3d.elements.U3dPoly):
        ...
    
    @property
    def diffuse_colors(self) -> aspose.cad.fileformats.u3d.elements.U3dPoly:
        ...
    
    @diffuse_colors.setter
    def diffuse_colors(self, value : aspose.cad.fileformats.u3d.elements.U3dPoly):
        ...
    
    @property
    def specular_colors(self) -> aspose.cad.fileformats.u3d.elements.U3dPoly:
        ...
    
    @specular_colors.setter
    def specular_colors(self, value : aspose.cad.fileformats.u3d.elements.U3dPoly):
        ...
    
    @property
    def tex_coords(self) -> aspose.cad.fileformats.u3d.elements.U3dPoly:
        ...
    
    @tex_coords.setter
    def tex_coords(self, value : aspose.cad.fileformats.u3d.elements.U3dPoly):
        ...
    
    ...

class U3dLine:
    
    def indexer_get(self, index : int) -> int:
        ...
    
    def indexer_set(self, index : int, value : int) -> None:
        ...
    
    @property
    def a(self) -> int:
        ...
    
    @a.setter
    def a(self, value : int):
        ...
    
    @property
    def b(self) -> int:
        ...
    
    @b.setter
    def b(self, value : int):
        ...
    
    def __getitem__(self, key : int) -> int:
        ...
    
    def __setitem__(self, key : int, value : int):
        ...
    
    ...

class U3dPoly:
    
    def indexer_get(self, index : int) -> int:
        ...
    
    def indexer_set(self, index : int, value : int) -> None:
        ...
    
    @property
    def a(self) -> int:
        ...
    
    @a.setter
    def a(self, value : int):
        ...
    
    @property
    def b(self) -> int:
        ...
    
    @b.setter
    def b(self, value : int):
        ...
    
    @property
    def c(self) -> int:
        ...
    
    @c.setter
    def c(self, value : int):
        ...
    
    def __getitem__(self, key : int) -> int:
        ...
    
    def __setitem__(self, key : int, value : int):
        ...
    
    ...

class U3dPositionConnectivity:
    '''The position connectivity used by line set analyzer.'''
    
    @property
    def line_index(self) -> List[int]:
        ...
    
    @line_index.setter
    def line_index(self, value : List[int]):
        ...
    
    @property
    def end_pos_index(self) -> List[int]:
        ...
    
    @end_pos_index.setter
    def end_pos_index(self, value : List[int]):
        ...
    
    @property
    def line_count(self) -> int:
        ...
    
    @line_count.setter
    def line_count(self, value : int):
        ...
    
    ...

class UIntDescending:
    '''Defines a custom comparer for uint type
    to sort elements in descending order.'''
    
    def compare(self, x : int, y : int) -> int:
        ...
    
    ...

