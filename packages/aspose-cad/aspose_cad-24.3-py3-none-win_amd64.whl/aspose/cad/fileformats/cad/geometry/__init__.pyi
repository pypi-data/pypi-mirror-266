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

class ICadGeometry:
    '''ICadGeometry class'''
    
    def convert_geometry_to_cad_entities(self) -> List[aspose.cad.fileformats.cad.cadobjects.CadEntityBase]:
        '''Converts the geometry to cad entities.'''
        ...
    
    def calculate_geometry_cad_entities(self) -> int:
        '''Calculates the geometry cad entities.'''
        ...
    
    def process_geometry_line_type(self, lt_dict : aspose.cad.fileformats.cad.CadLineTypesDictionary) -> None:
        '''Processes the type of the geometry line.
        
        :param lt_dict: The lt dictionary.'''
        ...
    
    def process_geometry_text_style(self, styles_list : aspose.cad.fileformats.cad.CadStylesList) -> None:
        '''Processes the geometry text style.
        
        :param styles_list: The styles list.'''
        ...
    
    @property
    def start_handle(self) -> int:
        ...
    
    @start_handle.setter
    def start_handle(self, value : int):
        ...
    
    ...

class ICadGeometryPolyline(ICadGeometry):
    
    def convert_geometry_to_cad_entities(self) -> List[aspose.cad.fileformats.cad.cadobjects.CadEntityBase]:
        '''Converts the geometry to cad entities.'''
        ...
    
    def calculate_geometry_cad_entities(self) -> int:
        '''Calculates the geometry cad entities.'''
        ...
    
    def process_geometry_line_type(self, lt_dict : aspose.cad.fileformats.cad.CadLineTypesDictionary) -> None:
        '''Processes the type of the geometry line.
        
        :param lt_dict: The lt dictionary.'''
        ...
    
    def process_geometry_text_style(self, styles_list : aspose.cad.fileformats.cad.CadStylesList) -> None:
        '''Processes the geometry text style.
        
        :param styles_list: The styles list.'''
        ...
    
    @property
    def line_style_name(self) -> str:
        ...
    
    @line_style_name.setter
    def line_style_name(self, value : str):
        ...
    
    @property
    def start_handle(self) -> int:
        ...
    
    @start_handle.setter
    def start_handle(self, value : int):
        ...
    
    ...

class ICadGeometryText(ICadGeometry):
    
    def convert_geometry_to_cad_entities(self) -> List[aspose.cad.fileformats.cad.cadobjects.CadEntityBase]:
        '''Converts the geometry to cad entities.'''
        ...
    
    def calculate_geometry_cad_entities(self) -> int:
        '''Calculates the geometry cad entities.'''
        ...
    
    def process_geometry_line_type(self, lt_dict : aspose.cad.fileformats.cad.CadLineTypesDictionary) -> None:
        '''Processes the type of the geometry line.
        
        :param lt_dict: The lt dictionary.'''
        ...
    
    def process_geometry_text_style(self, styles_list : aspose.cad.fileformats.cad.CadStylesList) -> None:
        '''Processes the geometry text style.
        
        :param styles_list: The styles list.'''
        ...
    
    @property
    def text(self) -> str:
        '''Gets the text.'''
        ...
    
    @text.setter
    def text(self, value : str):
        '''Sets the text.'''
        ...
    
    @property
    def size(self) -> float:
        '''Gets the size.'''
        ...
    
    @size.setter
    def size(self, value : float):
        '''Sets the size.'''
        ...
    
    @property
    def rotation(self) -> float:
        '''Gets the rotation.'''
        ...
    
    @rotation.setter
    def rotation(self, value : float):
        '''Sets the rotation.'''
        ...
    
    @property
    def color(self) -> aspose.cad.Color:
        '''Gets the color.'''
        ...
    
    @color.setter
    def color(self, value : aspose.cad.Color):
        '''Sets the color.'''
        ...
    
    @property
    def font_name(self) -> str:
        ...
    
    @font_name.setter
    def font_name(self, value : str):
        ...
    
    @property
    def font_file(self) -> str:
        ...
    
    @font_file.setter
    def font_file(self, value : str):
        ...
    
    @property
    def start_handle(self) -> int:
        ...
    
    @start_handle.setter
    def start_handle(self, value : int):
        ...
    
    ...

