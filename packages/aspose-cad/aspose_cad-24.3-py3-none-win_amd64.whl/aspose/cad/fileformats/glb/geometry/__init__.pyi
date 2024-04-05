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

class BaseBuilder:
    
    @property
    def name(self) -> str:
        '''Gets the display text name, or null.
        
        **⚠️ DO NOT USE AS AN OBJECT ID ⚠️** see remarks.'''
        ...
    
    @name.setter
    def name(self, value : str):
        '''Sets the display text name, or null.
        
        **⚠️ DO NOT USE AS AN OBJECT ID ⚠️** see remarks.'''
        ...
    
    @property
    def extras(self) -> aspose.cad.fileformats.glb.io.JsonContent:
        '''Gets the custom data of this object.'''
        ...
    
    @extras.setter
    def extras(self, value : aspose.cad.fileformats.glb.io.JsonContent):
        '''Sets the custom data of this object.'''
        ...
    
    ...

class IMorphTargetBuilder:
    '''Represents the vertex deltas of a specific morph target.
    :py:func:`Aspose.CAD.FileFormats.GLB.Geometry.IMeshBuilder`1.UseMorphTarget`'''
    
    @overload
    def set_vertex(self, mesh_vertex : aspose.cad.fileformats.glb.geometry.vertextypes.IVertexGeometry, morph_vertex : aspose.cad.fileformats.glb.geometry.vertextypes.IVertexGeometry) -> None:
        '''Sets an absolute morph target.
        
        :param mesh_vertex: The base mesh vertex to morph.
        :param morph_vertex: The morphed vertex.'''
        ...
    
    @overload
    def set_vertex(self, mesh_vertex : aspose.cad.fileformats.glb.geometry.vertextypes.IVertexGeometry, morph_vertex : aspose.cad.fileformats.glb.geometry.vertextypes.IVertexGeometry, morph_material : aspose.cad.fileformats.glb.geometry.vertextypes.IVertexMaterial) -> None:
        '''Sets an absolute morph target.
        
        :param mesh_vertex: The base mesh vertex to morph.
        :param morph_vertex: The morphed vertex.
        :param morph_material: The morphed vertex material.'''
        ...
    
    @overload
    def set_vertex_delta(self, mesh_vertex : aspose.cad.fileformats.glb.geometry.vertextypes.IVertexGeometry, geometry_delta : aspose.cad.fileformats.glb.geometry.vertextypes.VertexGeometryDelta) -> None:
        '''Sets a relative morph target
        
        :param mesh_vertex: The base mesh vertex to morph.
        :param geometry_delta: The offset from ``meshVertex`` to morph.'''
        ...
    
    @overload
    def set_vertex_delta(self, mesh_vertex : aspose.cad.fileformats.glb.geometry.vertextypes.IVertexGeometry, geometry_delta : aspose.cad.fileformats.glb.geometry.vertextypes.VertexGeometryDelta, material_delta : aspose.cad.fileformats.glb.geometry.vertextypes.VertexMaterialDelta) -> None:
        '''Sets a relative morph target
        
        :param mesh_vertex: The base mesh vertex to morph.
        :param geometry_delta: The offset from ``meshVertex`` to morph.
        :param material_delta: The offset from ``meshVertex`` material to morph.'''
        ...
    
    @property
    def vertices(self) -> List[aspose.cad.fileformats.glb.geometry.vertextypes.IVertexGeometry]:
        '''Gets the collection of vertex geometry parts in the base mesh'''
        ...
    
    ...

class VertexBufferColumns:
    '''Represents a vertex buffer, where every vertex attribute is represented as a vector column.'''
    
    def isolate_columns(self) -> None:
        '''Performs an in-place copy of the contents of every column,
        which guarantees that the columns of this :py:class:`aspose.cad.fileformats.glb.geometry.VertexBufferColumns`
        are not shared by any other object and can be modified safely.'''
        ...
    
    def with_transform(self, transform : aspose.cad.fileformats.glb.transforms.IGeometryTransform) -> aspose.cad.fileformats.glb.geometry.VertexBufferColumns:
        ...
    
    def add_morph_target(self) -> aspose.cad.fileformats.glb.geometry.VertexBufferColumns:
        ...
    
    def get_compatible_vertex_type(self) -> Type:
        ...
    
    @property
    def morph_targets(self) -> List[aspose.cad.fileformats.glb.geometry.VertexBufferColumns]:
        ...
    
    ...

