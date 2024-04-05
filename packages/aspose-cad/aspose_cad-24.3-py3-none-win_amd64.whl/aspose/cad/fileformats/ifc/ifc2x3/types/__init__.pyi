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

class IfcAbsorbedDoseMeasure(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcAbsorbedDoseMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcAccelerationMeasure(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcAccelerationMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcActorSelect(aspose.cad.fileformats.ifc.IfcSelect):
    '''IfcActorSelect'''
    
    @property
    def value(self) -> any:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value.'''
        ...
    
    ...

class IfcAmountOfSubstanceMeasure(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcAmountOfSubstanceMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcAngularVelocityMeasure(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcAngularVelocityMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcAppliedValueSelect(aspose.cad.fileformats.ifc.IfcSelect):
    '''IfcAppliedValueSelect'''
    
    @property
    def value(self) -> any:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value.'''
        ...
    
    ...

class IfcAreaMeasure(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcAreaMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcAxis2Placement(aspose.cad.fileformats.ifc.IfcSelect):
    '''IfcAxis2Placement'''
    
    @property
    def value(self) -> any:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value.'''
        ...
    
    ...

class IfcBoolean(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcBoolean'''
    
    @property
    def value(self) -> bool:
        ...
    
    @value.setter
    def value(self, value : bool):
        ...
    
    ...

class IfcBooleanOperand(aspose.cad.fileformats.ifc.IfcSelect):
    '''IfcBooleanOperand'''
    
    @property
    def value(self) -> any:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value.'''
        ...
    
    ...

class IfcBoxAlignment(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcBoxAlignment'''
    
    @property
    def value(self) -> aspose.cad.fileformats.ifc.ifc2x3.types.IfcLabel:
        ...
    
    @value.setter
    def value(self, value : aspose.cad.fileformats.ifc.ifc2x3.types.IfcLabel):
        ...
    
    ...

class IfcCharacterStyleSelect(aspose.cad.fileformats.ifc.IfcSelect):
    '''IfcCharacterStyleSelect'''
    
    @property
    def value(self) -> any:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value.'''
        ...
    
    ...

class IfcClassificationNotationSelect(aspose.cad.fileformats.ifc.IfcSelect):
    '''IfcClassificationNotationSelect'''
    
    @property
    def value(self) -> any:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value.'''
        ...
    
    ...

class IfcColour(aspose.cad.fileformats.ifc.IfcSelect):
    '''IfcColour'''
    
    @property
    def value(self) -> any:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value.'''
        ...
    
    ...

class IfcColourOrFactor(aspose.cad.fileformats.ifc.IfcSelect):
    '''IfcColourOrFactor'''
    
    @property
    def value(self) -> any:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value.'''
        ...
    
    ...

class IfcComplexNumber(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcComplexNumber'''
    
    ...

class IfcCompoundPlaneAngleMeasure(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcCompoundPlaneAngleMeasure'''
    
    ...

class IfcConditionCriterionSelect(aspose.cad.fileformats.ifc.IfcSelect):
    '''IfcConditionCriterionSelect'''
    
    @property
    def value(self) -> any:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value.'''
        ...
    
    ...

class IfcContextDependentMeasure(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcContextDependentMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcCountMeasure(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcCountMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcCsgSelect(aspose.cad.fileformats.ifc.IfcSelect):
    '''IfcCsgSelect'''
    
    @property
    def value(self) -> any:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value.'''
        ...
    
    ...

class IfcCurvatureMeasure(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcCurvatureMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcCurveFontOrScaledCurveFontSelect(aspose.cad.fileformats.ifc.IfcSelect):
    '''IfcCurveFontOrScaledCurveFontSelect'''
    
    @property
    def value(self) -> any:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value.'''
        ...
    
    ...

class IfcCurveOrEdgeCurve(aspose.cad.fileformats.ifc.IfcSelect):
    '''IfcCurveOrEdgeCurve'''
    
    @property
    def value(self) -> any:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value.'''
        ...
    
    ...

class IfcCurveStyleFontSelect(aspose.cad.fileformats.ifc.IfcSelect):
    '''IfcCurveStyleFontSelect'''
    
    @property
    def value(self) -> any:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value.'''
        ...
    
    ...

class IfcDateTimeSelect(aspose.cad.fileformats.ifc.IfcSelect):
    '''IfcDateTimeSelect'''
    
    @property
    def value(self) -> any:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value.'''
        ...
    
    ...

class IfcDayInMonthNumber(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcDayInMonthNumber'''
    
    @property
    def value(self) -> int:
        ...
    
    @value.setter
    def value(self, value : int):
        ...
    
    ...

class IfcDaylightSavingHour(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcDaylightSavingHour'''
    
    @property
    def value(self) -> int:
        ...
    
    @value.setter
    def value(self, value : int):
        ...
    
    ...

class IfcDefinedSymbolSelect(aspose.cad.fileformats.ifc.IfcSelect):
    '''IfcDefinedSymbolSelect'''
    
    @property
    def value(self) -> any:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value.'''
        ...
    
    ...

class IfcDerivedMeasureValue(aspose.cad.fileformats.ifc.IfcSelect):
    '''IfcDerivedMeasureValue'''
    
    @property
    def value(self) -> any:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value.'''
        ...
    
    ...

class IfcDescriptiveMeasure(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcDescriptiveMeasure'''
    
    @property
    def value(self) -> str:
        ...
    
    @value.setter
    def value(self, value : str):
        ...
    
    ...

class IfcDimensionCount(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcDimensionCount'''
    
    @property
    def value(self) -> int:
        ...
    
    @value.setter
    def value(self, value : int):
        ...
    
    ...

class IfcDocumentSelect(aspose.cad.fileformats.ifc.IfcSelect):
    '''IfcDocumentSelect'''
    
    @property
    def value(self) -> any:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value.'''
        ...
    
    ...

class IfcDoseEquivalentMeasure(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcDoseEquivalentMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcDraughtingCalloutElement(aspose.cad.fileformats.ifc.IfcSelect):
    '''IfcDraughtingCalloutElement'''
    
    @property
    def value(self) -> any:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value.'''
        ...
    
    ...

class IfcDynamicViscosityMeasure(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcDynamicViscosityMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcElectricCapacitanceMeasure(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcElectricCapacitanceMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcElectricChargeMeasure(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcElectricChargeMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcElectricConductanceMeasure(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcElectricConductanceMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcElectricCurrentMeasure(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcElectricCurrentMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcElectricResistanceMeasure(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcElectricResistanceMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcElectricVoltageMeasure(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcElectricVoltageMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcEnergyMeasure(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcEnergyMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcFillAreaStyleTileShapeSelect(aspose.cad.fileformats.ifc.IfcSelect):
    '''IfcFillAreaStyleTileShapeSelect'''
    
    @property
    def value(self) -> any:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value.'''
        ...
    
    ...

class IfcFillStyleSelect(aspose.cad.fileformats.ifc.IfcSelect):
    '''IfcFillStyleSelect'''
    
    @property
    def value(self) -> any:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value.'''
        ...
    
    ...

class IfcFontStyle(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcFontStyle'''
    
    @property
    def value(self) -> str:
        ...
    
    @value.setter
    def value(self, value : str):
        ...
    
    ...

class IfcFontVariant(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcFontVariant'''
    
    @property
    def value(self) -> str:
        ...
    
    @value.setter
    def value(self, value : str):
        ...
    
    ...

class IfcFontWeight(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcFontWeight'''
    
    @property
    def value(self) -> str:
        ...
    
    @value.setter
    def value(self, value : str):
        ...
    
    ...

class IfcForceMeasure(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcForceMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcFrequencyMeasure(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcFrequencyMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcGeometricSetSelect(aspose.cad.fileformats.ifc.IfcSelect):
    '''IfcGeometricSetSelect'''
    
    @property
    def value(self) -> any:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value.'''
        ...
    
    ...

class IfcGloballyUniqueId(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcGloballyUniqueId'''
    
    @property
    def value(self) -> str:
        ...
    
    @value.setter
    def value(self, value : str):
        ...
    
    ...

class IfcHatchLineDistanceSelect(aspose.cad.fileformats.ifc.IfcSelect):
    '''IfcHatchLineDistanceSelect'''
    
    @property
    def value(self) -> any:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value.'''
        ...
    
    ...

class IfcHeatFluxDensityMeasure(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcHeatFluxDensityMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcHeatingValueMeasure(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcHeatingValueMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcHourInDay(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcHourInDay'''
    
    @property
    def value(self) -> int:
        ...
    
    @value.setter
    def value(self, value : int):
        ...
    
    ...

class IfcIdentifier(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcIdentifier'''
    
    @property
    def value(self) -> str:
        ...
    
    @value.setter
    def value(self, value : str):
        ...
    
    ...

class IfcIlluminanceMeasure(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcIlluminanceMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcInductanceMeasure(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcInductanceMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcInteger(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcInteger'''
    
    @property
    def value(self) -> int:
        ...
    
    @value.setter
    def value(self, value : int):
        ...
    
    ...

class IfcIntegerCountRateMeasure(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcIntegerCountRateMeasure'''
    
    @property
    def value(self) -> int:
        ...
    
    @value.setter
    def value(self, value : int):
        ...
    
    ...

class IfcIonConcentrationMeasure(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcIonConcentrationMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcIsothermalMoistureCapacityMeasure(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcIsothermalMoistureCapacityMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcKinematicViscosityMeasure(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcKinematicViscosityMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcLabel(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcLabel'''
    
    @property
    def value(self) -> str:
        ...
    
    @value.setter
    def value(self, value : str):
        ...
    
    ...

class IfcLayeredItem(aspose.cad.fileformats.ifc.IfcSelect):
    '''IfcLayeredItem'''
    
    @property
    def value(self) -> any:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value.'''
        ...
    
    ...

class IfcLengthMeasure(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcLengthMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcLibrarySelect(aspose.cad.fileformats.ifc.IfcSelect):
    '''IfcLibrarySelect'''
    
    @property
    def value(self) -> any:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value.'''
        ...
    
    ...

class IfcLightDistributionDataSourceSelect(aspose.cad.fileformats.ifc.IfcSelect):
    '''IfcLightDistributionDataSourceSelect'''
    
    @property
    def value(self) -> any:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value.'''
        ...
    
    ...

class IfcLinearForceMeasure(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcLinearForceMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcLinearMomentMeasure(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcLinearMomentMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcLinearStiffnessMeasure(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcLinearStiffnessMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcLinearVelocityMeasure(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcLinearVelocityMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcLogical(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcLogical'''
    
    @property
    def value(self) -> Optional[bool]:
        ...
    
    @value.setter
    def value(self, value : Optional[bool]):
        ...
    
    ...

class IfcLuminousFluxMeasure(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcLuminousFluxMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcLuminousIntensityDistributionMeasure(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcLuminousIntensityDistributionMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcLuminousIntensityMeasure(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcLuminousIntensityMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcMagneticFluxDensityMeasure(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcMagneticFluxDensityMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcMagneticFluxMeasure(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcMagneticFluxMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcMassDensityMeasure(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcMassDensityMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcMassFlowRateMeasure(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcMassFlowRateMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcMassMeasure(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcMassMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcMassPerLengthMeasure(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcMassPerLengthMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcMaterialSelect(aspose.cad.fileformats.ifc.IfcSelect):
    '''IfcMaterialSelect'''
    
    @property
    def value(self) -> any:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value.'''
        ...
    
    ...

class IfcMeasureValue(aspose.cad.fileformats.ifc.IfcSelect):
    '''IfcMeasureValue'''
    
    @property
    def value(self) -> any:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value.'''
        ...
    
    ...

class IfcMetricValueSelect(aspose.cad.fileformats.ifc.IfcSelect):
    '''IfcMetricValueSelect'''
    
    @property
    def value(self) -> any:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value.'''
        ...
    
    ...

class IfcMinuteInHour(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcMinuteInHour'''
    
    @property
    def value(self) -> int:
        ...
    
    @value.setter
    def value(self, value : int):
        ...
    
    ...

class IfcModulusOfElasticityMeasure(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcModulusOfElasticityMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcModulusOfLinearSubgradeReactionMeasure(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcModulusOfLinearSubgradeReactionMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcModulusOfRotationalSubgradeReactionMeasure(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcModulusOfRotationalSubgradeReactionMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcModulusOfSubgradeReactionMeasure(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcModulusOfSubgradeReactionMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcMoistureDiffusivityMeasure(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcMoistureDiffusivityMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcMolecularWeightMeasure(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcMolecularWeightMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcMomentOfInertiaMeasure(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcMomentOfInertiaMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcMonetaryMeasure(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcMonetaryMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcMonthInYearNumber(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcMonthInYearNumber'''
    
    @property
    def value(self) -> int:
        ...
    
    @value.setter
    def value(self, value : int):
        ...
    
    ...

class IfcNormalisedRatioMeasure(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcNormalisedRatioMeasure'''
    
    @property
    def value(self) -> aspose.cad.fileformats.ifc.ifc2x3.types.IfcRatioMeasure:
        ...
    
    @value.setter
    def value(self, value : aspose.cad.fileformats.ifc.ifc2x3.types.IfcRatioMeasure):
        ...
    
    ...

class IfcNumericMeasure(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcNumericMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcObjectReferenceSelect(aspose.cad.fileformats.ifc.IfcSelect):
    '''IfcObjectReferenceSelect'''
    
    @property
    def value(self) -> any:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value.'''
        ...
    
    ...

class IfcOrientationSelect(aspose.cad.fileformats.ifc.IfcSelect):
    '''IfcOrientationSelect'''
    
    @property
    def value(self) -> any:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value.'''
        ...
    
    ...

class IfcPHMeasure(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcPHMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcParameterValue(aspose.cad.fileformats.ifc.IIfcType):
    '''Partial IIfc entity class'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcPlanarForceMeasure(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcPlanarForceMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcPlaneAngleMeasure(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcPlaneAngleMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcPointOrVertexPoint(aspose.cad.fileformats.ifc.IfcSelect):
    '''IfcPointOrVertexPoint'''
    
    @property
    def value(self) -> any:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value.'''
        ...
    
    ...

class IfcPositiveLengthMeasure(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcPositiveLengthMeasure'''
    
    @property
    def value(self) -> aspose.cad.fileformats.ifc.ifc2x3.types.IfcLengthMeasure:
        ...
    
    @value.setter
    def value(self, value : aspose.cad.fileformats.ifc.ifc2x3.types.IfcLengthMeasure):
        ...
    
    ...

class IfcPositivePlaneAngleMeasure(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcPositivePlaneAngleMeasure'''
    
    @property
    def value(self) -> aspose.cad.fileformats.ifc.ifc2x3.types.IfcPlaneAngleMeasure:
        ...
    
    @value.setter
    def value(self, value : aspose.cad.fileformats.ifc.ifc2x3.types.IfcPlaneAngleMeasure):
        ...
    
    ...

class IfcPositiveRatioMeasure(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcPositiveRatioMeasure'''
    
    @property
    def value(self) -> aspose.cad.fileformats.ifc.ifc2x3.types.IfcRatioMeasure:
        ...
    
    @value.setter
    def value(self, value : aspose.cad.fileformats.ifc.ifc2x3.types.IfcRatioMeasure):
        ...
    
    ...

class IfcPowerMeasure(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcPowerMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcPresentableText(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcPresentableText'''
    
    @property
    def value(self) -> str:
        ...
    
    @value.setter
    def value(self, value : str):
        ...
    
    ...

class IfcPresentationStyleSelect(aspose.cad.fileformats.ifc.IfcSelect):
    '''IfcPresentationStyleSelect'''
    
    @property
    def value(self) -> any:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value.'''
        ...
    
    ...

class IfcPressureMeasure(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcPressureMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcRadioActivityMeasure(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcRadioActivityMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcRatioMeasure(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcRatioMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcReal(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcReal'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcRotationalFrequencyMeasure(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcRotationalFrequencyMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcRotationalMassMeasure(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcRotationalMassMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcRotationalStiffnessMeasure(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcRotationalStiffnessMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcSecondInMinute(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcSecondInMinute'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcSectionModulusMeasure(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcSectionModulusMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcSectionalAreaIntegralMeasure(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcSectionalAreaIntegralMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcShearModulusMeasure(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcShearModulusMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcShell(aspose.cad.fileformats.ifc.IfcSelect):
    '''IfcShell'''
    
    @property
    def value(self) -> any:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value.'''
        ...
    
    ...

class IfcSimpleValue(aspose.cad.fileformats.ifc.IfcSelect):
    '''IfcSimpleValue'''
    
    @property
    def value(self) -> any:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value.'''
        ...
    
    ...

class IfcSizeSelect(aspose.cad.fileformats.ifc.IfcSelect):
    '''IfcSizeSelect'''
    
    @property
    def value(self) -> any:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value.'''
        ...
    
    ...

class IfcSolidAngleMeasure(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcSolidAngleMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcSoundPowerMeasure(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcSoundPowerMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcSoundPressureMeasure(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcSoundPressureMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcSpecificHeatCapacityMeasure(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcSpecificHeatCapacityMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcSpecularExponent(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcSpecularExponent'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcSpecularHighlightSelect(aspose.cad.fileformats.ifc.IfcSelect):
    '''IfcSpecularHighlightSelect'''
    
    @property
    def value(self) -> any:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value.'''
        ...
    
    ...

class IfcSpecularRoughness(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcSpecularRoughness'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcStructuralActivityAssignmentSelect(aspose.cad.fileformats.ifc.IfcSelect):
    '''IfcStructuralActivityAssignmentSelect'''
    
    @property
    def value(self) -> any:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value.'''
        ...
    
    ...

class IfcSurfaceOrFaceSurface(aspose.cad.fileformats.ifc.IfcSelect):
    '''IfcSurfaceOrFaceSurface'''
    
    @property
    def value(self) -> any:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value.'''
        ...
    
    ...

class IfcSurfaceStyleElementSelect(aspose.cad.fileformats.ifc.IfcSelect):
    '''IfcSurfaceStyleElementSelect'''
    
    @property
    def value(self) -> any:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value.'''
        ...
    
    ...

class IfcSymbolStyleSelect(aspose.cad.fileformats.ifc.IfcSelect):
    '''IfcSymbolStyleSelect'''
    
    @property
    def value(self) -> any:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value.'''
        ...
    
    ...

class IfcTemperatureGradientMeasure(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcTemperatureGradientMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcText(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcText'''
    
    @property
    def value(self) -> str:
        ...
    
    @value.setter
    def value(self, value : str):
        ...
    
    ...

class IfcTextAlignment(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcTextAlignment'''
    
    @property
    def value(self) -> str:
        ...
    
    @value.setter
    def value(self, value : str):
        ...
    
    ...

class IfcTextDecoration(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcTextDecoration'''
    
    @property
    def value(self) -> str:
        ...
    
    @value.setter
    def value(self, value : str):
        ...
    
    ...

class IfcTextFontName(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcTextFontName'''
    
    @property
    def value(self) -> str:
        ...
    
    @value.setter
    def value(self, value : str):
        ...
    
    ...

class IfcTextFontSelect(aspose.cad.fileformats.ifc.IfcSelect):
    '''IfcTextFontSelect'''
    
    @property
    def value(self) -> any:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value.'''
        ...
    
    ...

class IfcTextStyleSelect(aspose.cad.fileformats.ifc.IfcSelect):
    '''IfcTextStyleSelect'''
    
    @property
    def value(self) -> any:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value.'''
        ...
    
    ...

class IfcTextTransformation(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcTextTransformation'''
    
    @property
    def value(self) -> str:
        ...
    
    @value.setter
    def value(self, value : str):
        ...
    
    ...

class IfcThermalAdmittanceMeasure(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcThermalAdmittanceMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcThermalConductivityMeasure(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcThermalConductivityMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcThermalExpansionCoefficientMeasure(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcThermalExpansionCoefficientMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcThermalResistanceMeasure(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcThermalResistanceMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcThermalTransmittanceMeasure(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcThermalTransmittanceMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcThermodynamicTemperatureMeasure(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcThermodynamicTemperatureMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcTimeMeasure(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcTimeMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcTimeStamp(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcTimeStamp'''
    
    @property
    def value(self) -> int:
        ...
    
    @value.setter
    def value(self, value : int):
        ...
    
    ...

class IfcTorqueMeasure(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcTorqueMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcTrimmingSelect(aspose.cad.fileformats.ifc.IfcSelect):
    '''IfcTrimmingSelect'''
    
    @property
    def value(self) -> any:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value.'''
        ...
    
    ...

class IfcUnit(aspose.cad.fileformats.ifc.IfcSelect):
    '''IfcUnit'''
    
    @property
    def value(self) -> any:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value.'''
        ...
    
    ...

class IfcValue(aspose.cad.fileformats.ifc.IfcSelect):
    '''IfcValue'''
    
    @property
    def value(self) -> any:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value.'''
        ...
    
    ...

class IfcVaporPermeabilityMeasure(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcVaporPermeabilityMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcVectorOrDirection(aspose.cad.fileformats.ifc.IfcSelect):
    '''IfcVectorOrDirection'''
    
    @property
    def value(self) -> any:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value.'''
        ...
    
    ...

class IfcVolumeMeasure(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcVolumeMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcVolumetricFlowRateMeasure(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcVolumetricFlowRateMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcWarpingConstantMeasure(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcWarpingConstantMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcWarpingMomentMeasure(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcWarpingMomentMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcYearNumber(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcYearNumber'''
    
    @property
    def value(self) -> int:
        ...
    
    @value.setter
    def value(self, value : int):
        ...
    
    ...

class IfcActionSourceTypeEnum:
    '''IfcActionSourceTypeEnum'''
    
    @classmethod
    @property
    def DEAD_LOAD_G(cls) -> IfcActionSourceTypeEnum:
        ...
    
    @classmethod
    @property
    def COMPLETION_G1(cls) -> IfcActionSourceTypeEnum:
        ...
    
    @classmethod
    @property
    def LIVE_LOAD_Q(cls) -> IfcActionSourceTypeEnum:
        ...
    
    @classmethod
    @property
    def SNOW_S(cls) -> IfcActionSourceTypeEnum:
        ...
    
    @classmethod
    @property
    def WIND_W(cls) -> IfcActionSourceTypeEnum:
        ...
    
    @classmethod
    @property
    def PRESTRESSING_P(cls) -> IfcActionSourceTypeEnum:
        ...
    
    @classmethod
    @property
    def SETTLEMENT_U(cls) -> IfcActionSourceTypeEnum:
        ...
    
    @classmethod
    @property
    def TEMPERATURE_T(cls) -> IfcActionSourceTypeEnum:
        ...
    
    @classmethod
    @property
    def EARTHQUAKE_E(cls) -> IfcActionSourceTypeEnum:
        ...
    
    @classmethod
    @property
    def FIRE(cls) -> IfcActionSourceTypeEnum:
        ...
    
    @classmethod
    @property
    def IMPULSE(cls) -> IfcActionSourceTypeEnum:
        ...
    
    @classmethod
    @property
    def IMPACT(cls) -> IfcActionSourceTypeEnum:
        ...
    
    @classmethod
    @property
    def TRANSPORT(cls) -> IfcActionSourceTypeEnum:
        ...
    
    @classmethod
    @property
    def ERECTION(cls) -> IfcActionSourceTypeEnum:
        ...
    
    @classmethod
    @property
    def PROPPING(cls) -> IfcActionSourceTypeEnum:
        ...
    
    @classmethod
    @property
    def SYSTEM_IMPERFECTION(cls) -> IfcActionSourceTypeEnum:
        ...
    
    @classmethod
    @property
    def SHRINKAGE(cls) -> IfcActionSourceTypeEnum:
        ...
    
    @classmethod
    @property
    def CREEP(cls) -> IfcActionSourceTypeEnum:
        ...
    
    @classmethod
    @property
    def LACK_OF_FIT(cls) -> IfcActionSourceTypeEnum:
        ...
    
    @classmethod
    @property
    def BUOYANCY(cls) -> IfcActionSourceTypeEnum:
        ...
    
    @classmethod
    @property
    def ICE(cls) -> IfcActionSourceTypeEnum:
        ...
    
    @classmethod
    @property
    def CURRENT(cls) -> IfcActionSourceTypeEnum:
        ...
    
    @classmethod
    @property
    def WAVE(cls) -> IfcActionSourceTypeEnum:
        ...
    
    @classmethod
    @property
    def RAIN(cls) -> IfcActionSourceTypeEnum:
        ...
    
    @classmethod
    @property
    def BRAKES(cls) -> IfcActionSourceTypeEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcActionSourceTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcActionSourceTypeEnum:
        ...
    
    ...

class IfcActionTypeEnum:
    '''IfcActionTypeEnum'''
    
    @classmethod
    @property
    def PERMANENT_G(cls) -> IfcActionTypeEnum:
        ...
    
    @classmethod
    @property
    def VARIABLE_Q(cls) -> IfcActionTypeEnum:
        ...
    
    @classmethod
    @property
    def EXTRAORDINARY_A(cls) -> IfcActionTypeEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcActionTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcActionTypeEnum:
        ...
    
    ...

class IfcActuatorTypeEnum:
    '''IfcActuatorTypeEnum'''
    
    @classmethod
    @property
    def ELECTRICACTUATOR(cls) -> IfcActuatorTypeEnum:
        ...
    
    @classmethod
    @property
    def HANDOPERATEDACTUATOR(cls) -> IfcActuatorTypeEnum:
        ...
    
    @classmethod
    @property
    def HYDRAULICACTUATOR(cls) -> IfcActuatorTypeEnum:
        ...
    
    @classmethod
    @property
    def PNEUMATICACTUATOR(cls) -> IfcActuatorTypeEnum:
        ...
    
    @classmethod
    @property
    def THERMOSTATICACTUATOR(cls) -> IfcActuatorTypeEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcActuatorTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcActuatorTypeEnum:
        ...
    
    ...

class IfcAddressTypeEnum:
    '''IfcAddressTypeEnum'''
    
    @classmethod
    @property
    def OFFICE(cls) -> IfcAddressTypeEnum:
        ...
    
    @classmethod
    @property
    def SITE(cls) -> IfcAddressTypeEnum:
        ...
    
    @classmethod
    @property
    def HOME(cls) -> IfcAddressTypeEnum:
        ...
    
    @classmethod
    @property
    def DISTRIBUTIONPOINT(cls) -> IfcAddressTypeEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcAddressTypeEnum:
        ...
    
    ...

class IfcAheadOrBehind:
    '''IfcAheadOrBehind'''
    
    @classmethod
    @property
    def AHEAD(cls) -> IfcAheadOrBehind:
        ...
    
    @classmethod
    @property
    def BEHIND(cls) -> IfcAheadOrBehind:
        ...
    
    ...

class IfcAirTerminalBoxTypeEnum:
    '''IfcAirTerminalBoxTypeEnum'''
    
    @classmethod
    @property
    def CONSTANTFLOW(cls) -> IfcAirTerminalBoxTypeEnum:
        ...
    
    @classmethod
    @property
    def VARIABLEFLOWPRESSUREDEPENDANT(cls) -> IfcAirTerminalBoxTypeEnum:
        ...
    
    @classmethod
    @property
    def VARIABLEFLOWPRESSUREINDEPENDANT(cls) -> IfcAirTerminalBoxTypeEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcAirTerminalBoxTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcAirTerminalBoxTypeEnum:
        ...
    
    ...

class IfcAirTerminalTypeEnum:
    '''IfcAirTerminalTypeEnum'''
    
    @classmethod
    @property
    def GRILLE(cls) -> IfcAirTerminalTypeEnum:
        ...
    
    @classmethod
    @property
    def REGISTER(cls) -> IfcAirTerminalTypeEnum:
        ...
    
    @classmethod
    @property
    def DIFFUSER(cls) -> IfcAirTerminalTypeEnum:
        ...
    
    @classmethod
    @property
    def EYEBALL(cls) -> IfcAirTerminalTypeEnum:
        ...
    
    @classmethod
    @property
    def IRIS(cls) -> IfcAirTerminalTypeEnum:
        ...
    
    @classmethod
    @property
    def LINEARGRILLE(cls) -> IfcAirTerminalTypeEnum:
        ...
    
    @classmethod
    @property
    def LINEARDIFFUSER(cls) -> IfcAirTerminalTypeEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcAirTerminalTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcAirTerminalTypeEnum:
        ...
    
    ...

class IfcAirToAirHeatRecoveryTypeEnum:
    '''IfcAirToAirHeatRecoveryTypeEnum'''
    
    @classmethod
    @property
    def FIXEDPLATECOUNTERFLOWEXCHANGER(cls) -> IfcAirToAirHeatRecoveryTypeEnum:
        ...
    
    @classmethod
    @property
    def FIXEDPLATECROSSFLOWEXCHANGER(cls) -> IfcAirToAirHeatRecoveryTypeEnum:
        ...
    
    @classmethod
    @property
    def FIXEDPLATEPARALLELFLOWEXCHANGER(cls) -> IfcAirToAirHeatRecoveryTypeEnum:
        ...
    
    @classmethod
    @property
    def ROTARYWHEEL(cls) -> IfcAirToAirHeatRecoveryTypeEnum:
        ...
    
    @classmethod
    @property
    def RUNAROUNDCOILLOOP(cls) -> IfcAirToAirHeatRecoveryTypeEnum:
        ...
    
    @classmethod
    @property
    def HEATPIPE(cls) -> IfcAirToAirHeatRecoveryTypeEnum:
        ...
    
    @classmethod
    @property
    def TWINTOWERENTHALPYRECOVERYLOOPS(cls) -> IfcAirToAirHeatRecoveryTypeEnum:
        ...
    
    @classmethod
    @property
    def THERMOSIPHONSEALEDTUBEHEATEXCHANGERS(cls) -> IfcAirToAirHeatRecoveryTypeEnum:
        ...
    
    @classmethod
    @property
    def THERMOSIPHONCOILTYPEHEATEXCHANGERS(cls) -> IfcAirToAirHeatRecoveryTypeEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcAirToAirHeatRecoveryTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcAirToAirHeatRecoveryTypeEnum:
        ...
    
    ...

class IfcAlarmTypeEnum:
    '''IfcAlarmTypeEnum'''
    
    @classmethod
    @property
    def BELL(cls) -> IfcAlarmTypeEnum:
        ...
    
    @classmethod
    @property
    def BREAKGLASSBUTTON(cls) -> IfcAlarmTypeEnum:
        ...
    
    @classmethod
    @property
    def LIGHT(cls) -> IfcAlarmTypeEnum:
        ...
    
    @classmethod
    @property
    def MANUALPULLBOX(cls) -> IfcAlarmTypeEnum:
        ...
    
    @classmethod
    @property
    def SIREN(cls) -> IfcAlarmTypeEnum:
        ...
    
    @classmethod
    @property
    def WHISTLE(cls) -> IfcAlarmTypeEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcAlarmTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcAlarmTypeEnum:
        ...
    
    ...

class IfcAnalysisModelTypeEnum:
    '''IfcAnalysisModelTypeEnum'''
    
    @classmethod
    @property
    def IN_PLANE_LOADING_2D(cls) -> IfcAnalysisModelTypeEnum:
        ...
    
    @classmethod
    @property
    def OUT_PLANE_LOADING_2D(cls) -> IfcAnalysisModelTypeEnum:
        ...
    
    @classmethod
    @property
    def LOADING_3D(cls) -> IfcAnalysisModelTypeEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcAnalysisModelTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcAnalysisModelTypeEnum:
        ...
    
    ...

class IfcAnalysisTheoryTypeEnum:
    '''IfcAnalysisTheoryTypeEnum'''
    
    @classmethod
    @property
    def FIRST_ORDER_THEORY(cls) -> IfcAnalysisTheoryTypeEnum:
        ...
    
    @classmethod
    @property
    def SECOND_ORDER_THEORY(cls) -> IfcAnalysisTheoryTypeEnum:
        ...
    
    @classmethod
    @property
    def THIRD_ORDER_THEORY(cls) -> IfcAnalysisTheoryTypeEnum:
        ...
    
    @classmethod
    @property
    def FULL_NONLINEAR_THEORY(cls) -> IfcAnalysisTheoryTypeEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcAnalysisTheoryTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcAnalysisTheoryTypeEnum:
        ...
    
    ...

class IfcArithmeticOperatorEnum:
    '''IfcArithmeticOperatorEnum'''
    
    @classmethod
    @property
    def ADD(cls) -> IfcArithmeticOperatorEnum:
        ...
    
    @classmethod
    @property
    def DIVIDE(cls) -> IfcArithmeticOperatorEnum:
        ...
    
    @classmethod
    @property
    def MULTIPLY(cls) -> IfcArithmeticOperatorEnum:
        ...
    
    @classmethod
    @property
    def SUBTRACT(cls) -> IfcArithmeticOperatorEnum:
        ...
    
    ...

class IfcAssemblyPlaceEnum:
    '''IfcAssemblyPlaceEnum'''
    
    @classmethod
    @property
    def SITE(cls) -> IfcAssemblyPlaceEnum:
        ...
    
    @classmethod
    @property
    def FACTORY(cls) -> IfcAssemblyPlaceEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcAssemblyPlaceEnum:
        ...
    
    ...

class IfcBSplineCurveForm:
    '''IfcBSplineCurveForm'''
    
    @classmethod
    @property
    def POLYLINE_FORM(cls) -> IfcBSplineCurveForm:
        ...
    
    @classmethod
    @property
    def CIRCULAR_ARC(cls) -> IfcBSplineCurveForm:
        ...
    
    @classmethod
    @property
    def ELLIPTIC_ARC(cls) -> IfcBSplineCurveForm:
        ...
    
    @classmethod
    @property
    def PARABOLIC_ARC(cls) -> IfcBSplineCurveForm:
        ...
    
    @classmethod
    @property
    def HYPERBOLIC_ARC(cls) -> IfcBSplineCurveForm:
        ...
    
    @classmethod
    @property
    def UNSPECIFIED(cls) -> IfcBSplineCurveForm:
        ...
    
    ...

class IfcBeamTypeEnum:
    '''IfcBeamTypeEnum'''
    
    @classmethod
    @property
    def BEAM(cls) -> IfcBeamTypeEnum:
        ...
    
    @classmethod
    @property
    def JOIST(cls) -> IfcBeamTypeEnum:
        ...
    
    @classmethod
    @property
    def LINTEL(cls) -> IfcBeamTypeEnum:
        ...
    
    @classmethod
    @property
    def T_BEAM(cls) -> IfcBeamTypeEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcBeamTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcBeamTypeEnum:
        ...
    
    ...

class IfcBenchmarkEnum:
    '''IfcBenchmarkEnum'''
    
    @classmethod
    @property
    def GREATERTHAN(cls) -> IfcBenchmarkEnum:
        ...
    
    @classmethod
    @property
    def GREATERTHANOREQUALTO(cls) -> IfcBenchmarkEnum:
        ...
    
    @classmethod
    @property
    def LESSTHAN(cls) -> IfcBenchmarkEnum:
        ...
    
    @classmethod
    @property
    def LESSTHANOREQUALTO(cls) -> IfcBenchmarkEnum:
        ...
    
    @classmethod
    @property
    def EQUALTO(cls) -> IfcBenchmarkEnum:
        ...
    
    @classmethod
    @property
    def NOTEQUALTO(cls) -> IfcBenchmarkEnum:
        ...
    
    ...

class IfcBoilerTypeEnum:
    '''IfcBoilerTypeEnum'''
    
    @classmethod
    @property
    def WATER(cls) -> IfcBoilerTypeEnum:
        ...
    
    @classmethod
    @property
    def STEAM(cls) -> IfcBoilerTypeEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcBoilerTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcBoilerTypeEnum:
        ...
    
    ...

class IfcBooleanOperator:
    '''IfcBooleanOperator'''
    
    @classmethod
    @property
    def UNION(cls) -> IfcBooleanOperator:
        ...
    
    @classmethod
    @property
    def INTERSECTION(cls) -> IfcBooleanOperator:
        ...
    
    @classmethod
    @property
    def DIFFERENCE(cls) -> IfcBooleanOperator:
        ...
    
    ...

class IfcBuildingElementProxyTypeEnum:
    '''IfcBuildingElementProxyTypeEnum'''
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcBuildingElementProxyTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcBuildingElementProxyTypeEnum:
        ...
    
    ...

class IfcCableCarrierFittingTypeEnum:
    '''IfcCableCarrierFittingTypeEnum'''
    
    @classmethod
    @property
    def BEND(cls) -> IfcCableCarrierFittingTypeEnum:
        ...
    
    @classmethod
    @property
    def CROSS(cls) -> IfcCableCarrierFittingTypeEnum:
        ...
    
    @classmethod
    @property
    def REDUCER(cls) -> IfcCableCarrierFittingTypeEnum:
        ...
    
    @classmethod
    @property
    def TEE(cls) -> IfcCableCarrierFittingTypeEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcCableCarrierFittingTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcCableCarrierFittingTypeEnum:
        ...
    
    ...

class IfcCableCarrierSegmentTypeEnum:
    '''IfcCableCarrierSegmentTypeEnum'''
    
    @classmethod
    @property
    def CABLELADDERSEGMENT(cls) -> IfcCableCarrierSegmentTypeEnum:
        ...
    
    @classmethod
    @property
    def CABLETRAYSEGMENT(cls) -> IfcCableCarrierSegmentTypeEnum:
        ...
    
    @classmethod
    @property
    def CABLETRUNKINGSEGMENT(cls) -> IfcCableCarrierSegmentTypeEnum:
        ...
    
    @classmethod
    @property
    def CONDUITSEGMENT(cls) -> IfcCableCarrierSegmentTypeEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcCableCarrierSegmentTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcCableCarrierSegmentTypeEnum:
        ...
    
    ...

class IfcCableSegmentTypeEnum:
    '''IfcCableSegmentTypeEnum'''
    
    @classmethod
    @property
    def CABLESEGMENT(cls) -> IfcCableSegmentTypeEnum:
        ...
    
    @classmethod
    @property
    def CONDUCTORSEGMENT(cls) -> IfcCableSegmentTypeEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcCableSegmentTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcCableSegmentTypeEnum:
        ...
    
    ...

class IfcChangeActionEnum:
    '''IfcChangeActionEnum'''
    
    @classmethod
    @property
    def NOCHANGE(cls) -> IfcChangeActionEnum:
        ...
    
    @classmethod
    @property
    def MODIFIED(cls) -> IfcChangeActionEnum:
        ...
    
    @classmethod
    @property
    def ADDED(cls) -> IfcChangeActionEnum:
        ...
    
    @classmethod
    @property
    def DELETED(cls) -> IfcChangeActionEnum:
        ...
    
    @classmethod
    @property
    def MODIFIEDADDED(cls) -> IfcChangeActionEnum:
        ...
    
    @classmethod
    @property
    def MODIFIEDDELETED(cls) -> IfcChangeActionEnum:
        ...
    
    ...

class IfcChillerTypeEnum:
    '''IfcChillerTypeEnum'''
    
    @classmethod
    @property
    def AIRCOOLED(cls) -> IfcChillerTypeEnum:
        ...
    
    @classmethod
    @property
    def WATERCOOLED(cls) -> IfcChillerTypeEnum:
        ...
    
    @classmethod
    @property
    def HEATRECOVERY(cls) -> IfcChillerTypeEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcChillerTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcChillerTypeEnum:
        ...
    
    ...

class IfcCoilTypeEnum:
    '''IfcCoilTypeEnum'''
    
    @classmethod
    @property
    def DXCOOLINGCOIL(cls) -> IfcCoilTypeEnum:
        ...
    
    @classmethod
    @property
    def WATERCOOLINGCOIL(cls) -> IfcCoilTypeEnum:
        ...
    
    @classmethod
    @property
    def STEAMHEATINGCOIL(cls) -> IfcCoilTypeEnum:
        ...
    
    @classmethod
    @property
    def WATERHEATINGCOIL(cls) -> IfcCoilTypeEnum:
        ...
    
    @classmethod
    @property
    def ELECTRICHEATINGCOIL(cls) -> IfcCoilTypeEnum:
        ...
    
    @classmethod
    @property
    def GASHEATINGCOIL(cls) -> IfcCoilTypeEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcCoilTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcCoilTypeEnum:
        ...
    
    ...

class IfcColumnTypeEnum:
    '''IfcColumnTypeEnum'''
    
    @classmethod
    @property
    def COLUMN(cls) -> IfcColumnTypeEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcColumnTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcColumnTypeEnum:
        ...
    
    ...

class IfcCompressorTypeEnum:
    '''IfcCompressorTypeEnum'''
    
    @classmethod
    @property
    def DYNAMIC(cls) -> IfcCompressorTypeEnum:
        ...
    
    @classmethod
    @property
    def RECIPROCATING(cls) -> IfcCompressorTypeEnum:
        ...
    
    @classmethod
    @property
    def ROTARY(cls) -> IfcCompressorTypeEnum:
        ...
    
    @classmethod
    @property
    def SCROLL(cls) -> IfcCompressorTypeEnum:
        ...
    
    @classmethod
    @property
    def TROCHOIDAL(cls) -> IfcCompressorTypeEnum:
        ...
    
    @classmethod
    @property
    def SINGLESTAGE(cls) -> IfcCompressorTypeEnum:
        ...
    
    @classmethod
    @property
    def BOOSTER(cls) -> IfcCompressorTypeEnum:
        ...
    
    @classmethod
    @property
    def OPENTYPE(cls) -> IfcCompressorTypeEnum:
        ...
    
    @classmethod
    @property
    def HERMETIC(cls) -> IfcCompressorTypeEnum:
        ...
    
    @classmethod
    @property
    def SEMIHERMETIC(cls) -> IfcCompressorTypeEnum:
        ...
    
    @classmethod
    @property
    def WELDEDSHELLHERMETIC(cls) -> IfcCompressorTypeEnum:
        ...
    
    @classmethod
    @property
    def ROLLINGPISTON(cls) -> IfcCompressorTypeEnum:
        ...
    
    @classmethod
    @property
    def ROTARYVANE(cls) -> IfcCompressorTypeEnum:
        ...
    
    @classmethod
    @property
    def SINGLESCREW(cls) -> IfcCompressorTypeEnum:
        ...
    
    @classmethod
    @property
    def TWINSCREW(cls) -> IfcCompressorTypeEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcCompressorTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcCompressorTypeEnum:
        ...
    
    ...

class IfcCondenserTypeEnum:
    '''IfcCondenserTypeEnum'''
    
    @classmethod
    @property
    def WATERCOOLEDSHELLTUBE(cls) -> IfcCondenserTypeEnum:
        ...
    
    @classmethod
    @property
    def WATERCOOLEDSHELLCOIL(cls) -> IfcCondenserTypeEnum:
        ...
    
    @classmethod
    @property
    def WATERCOOLEDTUBEINTUBE(cls) -> IfcCondenserTypeEnum:
        ...
    
    @classmethod
    @property
    def WATERCOOLEDBRAZEDPLATE(cls) -> IfcCondenserTypeEnum:
        ...
    
    @classmethod
    @property
    def AIRCOOLED(cls) -> IfcCondenserTypeEnum:
        ...
    
    @classmethod
    @property
    def EVAPORATIVECOOLED(cls) -> IfcCondenserTypeEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcCondenserTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcCondenserTypeEnum:
        ...
    
    ...

class IfcConnectionTypeEnum:
    '''IfcConnectionTypeEnum'''
    
    @classmethod
    @property
    def ATPATH(cls) -> IfcConnectionTypeEnum:
        ...
    
    @classmethod
    @property
    def ATSTART(cls) -> IfcConnectionTypeEnum:
        ...
    
    @classmethod
    @property
    def ATEND(cls) -> IfcConnectionTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcConnectionTypeEnum:
        ...
    
    ...

class IfcConstraintEnum:
    '''IfcConstraintEnum'''
    
    @classmethod
    @property
    def HARD(cls) -> IfcConstraintEnum:
        ...
    
    @classmethod
    @property
    def SOFT(cls) -> IfcConstraintEnum:
        ...
    
    @classmethod
    @property
    def ADVISORY(cls) -> IfcConstraintEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcConstraintEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcConstraintEnum:
        ...
    
    ...

class IfcControllerTypeEnum:
    '''IfcControllerTypeEnum'''
    
    @classmethod
    @property
    def FLOATING(cls) -> IfcControllerTypeEnum:
        ...
    
    @classmethod
    @property
    def PROPORTIONAL(cls) -> IfcControllerTypeEnum:
        ...
    
    @classmethod
    @property
    def PROPORTIONALINTEGRAL(cls) -> IfcControllerTypeEnum:
        ...
    
    @classmethod
    @property
    def PROPORTIONALINTEGRALDERIVATIVE(cls) -> IfcControllerTypeEnum:
        ...
    
    @classmethod
    @property
    def TIMEDTWOPOSITION(cls) -> IfcControllerTypeEnum:
        ...
    
    @classmethod
    @property
    def TWOPOSITION(cls) -> IfcControllerTypeEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcControllerTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcControllerTypeEnum:
        ...
    
    ...

class IfcCooledBeamTypeEnum:
    '''IfcCooledBeamTypeEnum'''
    
    @classmethod
    @property
    def ACTIVE(cls) -> IfcCooledBeamTypeEnum:
        ...
    
    @classmethod
    @property
    def PASSIVE(cls) -> IfcCooledBeamTypeEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcCooledBeamTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcCooledBeamTypeEnum:
        ...
    
    ...

class IfcCoolingTowerTypeEnum:
    '''IfcCoolingTowerTypeEnum'''
    
    @classmethod
    @property
    def NATURALDRAFT(cls) -> IfcCoolingTowerTypeEnum:
        ...
    
    @classmethod
    @property
    def MECHANICALINDUCEDDRAFT(cls) -> IfcCoolingTowerTypeEnum:
        ...
    
    @classmethod
    @property
    def MECHANICALFORCEDDRAFT(cls) -> IfcCoolingTowerTypeEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcCoolingTowerTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcCoolingTowerTypeEnum:
        ...
    
    ...

class IfcCostScheduleTypeEnum:
    '''IfcCostScheduleTypeEnum'''
    
    @classmethod
    @property
    def BUDGET(cls) -> IfcCostScheduleTypeEnum:
        ...
    
    @classmethod
    @property
    def COSTPLAN(cls) -> IfcCostScheduleTypeEnum:
        ...
    
    @classmethod
    @property
    def ESTIMATE(cls) -> IfcCostScheduleTypeEnum:
        ...
    
    @classmethod
    @property
    def TENDER(cls) -> IfcCostScheduleTypeEnum:
        ...
    
    @classmethod
    @property
    def PRICEDBILLOFQUANTITIES(cls) -> IfcCostScheduleTypeEnum:
        ...
    
    @classmethod
    @property
    def UNPRICEDBILLOFQUANTITIES(cls) -> IfcCostScheduleTypeEnum:
        ...
    
    @classmethod
    @property
    def SCHEDULEOFRATES(cls) -> IfcCostScheduleTypeEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcCostScheduleTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcCostScheduleTypeEnum:
        ...
    
    ...

class IfcCoveringTypeEnum:
    '''IfcCoveringTypeEnum'''
    
    @classmethod
    @property
    def CEILING(cls) -> IfcCoveringTypeEnum:
        ...
    
    @classmethod
    @property
    def FLOORING(cls) -> IfcCoveringTypeEnum:
        ...
    
    @classmethod
    @property
    def CLADDING(cls) -> IfcCoveringTypeEnum:
        ...
    
    @classmethod
    @property
    def ROOFING(cls) -> IfcCoveringTypeEnum:
        ...
    
    @classmethod
    @property
    def INSULATION(cls) -> IfcCoveringTypeEnum:
        ...
    
    @classmethod
    @property
    def MEMBRANE(cls) -> IfcCoveringTypeEnum:
        ...
    
    @classmethod
    @property
    def SLEEVING(cls) -> IfcCoveringTypeEnum:
        ...
    
    @classmethod
    @property
    def WRAPPING(cls) -> IfcCoveringTypeEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcCoveringTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcCoveringTypeEnum:
        ...
    
    ...

class IfcCurrencyEnum:
    '''IfcCurrencyEnum'''
    
    @classmethod
    @property
    def AED(cls) -> IfcCurrencyEnum:
        ...
    
    @classmethod
    @property
    def AES(cls) -> IfcCurrencyEnum:
        ...
    
    @classmethod
    @property
    def ATS(cls) -> IfcCurrencyEnum:
        ...
    
    @classmethod
    @property
    def AUD(cls) -> IfcCurrencyEnum:
        ...
    
    @classmethod
    @property
    def BBD(cls) -> IfcCurrencyEnum:
        ...
    
    @classmethod
    @property
    def BEG(cls) -> IfcCurrencyEnum:
        ...
    
    @classmethod
    @property
    def BGL(cls) -> IfcCurrencyEnum:
        ...
    
    @classmethod
    @property
    def BHD(cls) -> IfcCurrencyEnum:
        ...
    
    @classmethod
    @property
    def BMD(cls) -> IfcCurrencyEnum:
        ...
    
    @classmethod
    @property
    def BND(cls) -> IfcCurrencyEnum:
        ...
    
    @classmethod
    @property
    def BRL(cls) -> IfcCurrencyEnum:
        ...
    
    @classmethod
    @property
    def BSD(cls) -> IfcCurrencyEnum:
        ...
    
    @classmethod
    @property
    def BWP(cls) -> IfcCurrencyEnum:
        ...
    
    @classmethod
    @property
    def BZD(cls) -> IfcCurrencyEnum:
        ...
    
    @classmethod
    @property
    def CAD(cls) -> IfcCurrencyEnum:
        ...
    
    @classmethod
    @property
    def CBD(cls) -> IfcCurrencyEnum:
        ...
    
    @classmethod
    @property
    def CHF(cls) -> IfcCurrencyEnum:
        ...
    
    @classmethod
    @property
    def CLP(cls) -> IfcCurrencyEnum:
        ...
    
    @classmethod
    @property
    def CNY(cls) -> IfcCurrencyEnum:
        ...
    
    @classmethod
    @property
    def CYS(cls) -> IfcCurrencyEnum:
        ...
    
    @classmethod
    @property
    def CZK(cls) -> IfcCurrencyEnum:
        ...
    
    @classmethod
    @property
    def DDP(cls) -> IfcCurrencyEnum:
        ...
    
    @classmethod
    @property
    def DEM(cls) -> IfcCurrencyEnum:
        ...
    
    @classmethod
    @property
    def DKK(cls) -> IfcCurrencyEnum:
        ...
    
    @classmethod
    @property
    def EGL(cls) -> IfcCurrencyEnum:
        ...
    
    @classmethod
    @property
    def EST(cls) -> IfcCurrencyEnum:
        ...
    
    @classmethod
    @property
    def EUR(cls) -> IfcCurrencyEnum:
        ...
    
    @classmethod
    @property
    def FAK(cls) -> IfcCurrencyEnum:
        ...
    
    @classmethod
    @property
    def FIM(cls) -> IfcCurrencyEnum:
        ...
    
    @classmethod
    @property
    def FJD(cls) -> IfcCurrencyEnum:
        ...
    
    @classmethod
    @property
    def FKP(cls) -> IfcCurrencyEnum:
        ...
    
    @classmethod
    @property
    def FRF(cls) -> IfcCurrencyEnum:
        ...
    
    @classmethod
    @property
    def GBP(cls) -> IfcCurrencyEnum:
        ...
    
    @classmethod
    @property
    def GIP(cls) -> IfcCurrencyEnum:
        ...
    
    @classmethod
    @property
    def GMD(cls) -> IfcCurrencyEnum:
        ...
    
    @classmethod
    @property
    def GRX(cls) -> IfcCurrencyEnum:
        ...
    
    @classmethod
    @property
    def HKD(cls) -> IfcCurrencyEnum:
        ...
    
    @classmethod
    @property
    def HUF(cls) -> IfcCurrencyEnum:
        ...
    
    @classmethod
    @property
    def ICK(cls) -> IfcCurrencyEnum:
        ...
    
    @classmethod
    @property
    def IDR(cls) -> IfcCurrencyEnum:
        ...
    
    @classmethod
    @property
    def ILS(cls) -> IfcCurrencyEnum:
        ...
    
    @classmethod
    @property
    def INR(cls) -> IfcCurrencyEnum:
        ...
    
    @classmethod
    @property
    def IRP(cls) -> IfcCurrencyEnum:
        ...
    
    @classmethod
    @property
    def ITL(cls) -> IfcCurrencyEnum:
        ...
    
    @classmethod
    @property
    def JMD(cls) -> IfcCurrencyEnum:
        ...
    
    @classmethod
    @property
    def JOD(cls) -> IfcCurrencyEnum:
        ...
    
    @classmethod
    @property
    def JPY(cls) -> IfcCurrencyEnum:
        ...
    
    @classmethod
    @property
    def KES(cls) -> IfcCurrencyEnum:
        ...
    
    @classmethod
    @property
    def KRW(cls) -> IfcCurrencyEnum:
        ...
    
    @classmethod
    @property
    def KWD(cls) -> IfcCurrencyEnum:
        ...
    
    @classmethod
    @property
    def KYD(cls) -> IfcCurrencyEnum:
        ...
    
    @classmethod
    @property
    def LKR(cls) -> IfcCurrencyEnum:
        ...
    
    @classmethod
    @property
    def LUF(cls) -> IfcCurrencyEnum:
        ...
    
    @classmethod
    @property
    def MTL(cls) -> IfcCurrencyEnum:
        ...
    
    @classmethod
    @property
    def MUR(cls) -> IfcCurrencyEnum:
        ...
    
    @classmethod
    @property
    def MXN(cls) -> IfcCurrencyEnum:
        ...
    
    @classmethod
    @property
    def MYR(cls) -> IfcCurrencyEnum:
        ...
    
    @classmethod
    @property
    def NLG(cls) -> IfcCurrencyEnum:
        ...
    
    @classmethod
    @property
    def NZD(cls) -> IfcCurrencyEnum:
        ...
    
    @classmethod
    @property
    def OMR(cls) -> IfcCurrencyEnum:
        ...
    
    @classmethod
    @property
    def PGK(cls) -> IfcCurrencyEnum:
        ...
    
    @classmethod
    @property
    def PHP(cls) -> IfcCurrencyEnum:
        ...
    
    @classmethod
    @property
    def PKR(cls) -> IfcCurrencyEnum:
        ...
    
    @classmethod
    @property
    def PLN(cls) -> IfcCurrencyEnum:
        ...
    
    @classmethod
    @property
    def PTN(cls) -> IfcCurrencyEnum:
        ...
    
    @classmethod
    @property
    def QAR(cls) -> IfcCurrencyEnum:
        ...
    
    @classmethod
    @property
    def RUR(cls) -> IfcCurrencyEnum:
        ...
    
    @classmethod
    @property
    def SAR(cls) -> IfcCurrencyEnum:
        ...
    
    @classmethod
    @property
    def SCR(cls) -> IfcCurrencyEnum:
        ...
    
    @classmethod
    @property
    def SEK(cls) -> IfcCurrencyEnum:
        ...
    
    @classmethod
    @property
    def SGD(cls) -> IfcCurrencyEnum:
        ...
    
    @classmethod
    @property
    def SKP(cls) -> IfcCurrencyEnum:
        ...
    
    @classmethod
    @property
    def THB(cls) -> IfcCurrencyEnum:
        ...
    
    @classmethod
    @property
    def TRL(cls) -> IfcCurrencyEnum:
        ...
    
    @classmethod
    @property
    def TTD(cls) -> IfcCurrencyEnum:
        ...
    
    @classmethod
    @property
    def TWD(cls) -> IfcCurrencyEnum:
        ...
    
    @classmethod
    @property
    def USD(cls) -> IfcCurrencyEnum:
        ...
    
    @classmethod
    @property
    def VEB(cls) -> IfcCurrencyEnum:
        ...
    
    @classmethod
    @property
    def VND(cls) -> IfcCurrencyEnum:
        ...
    
    @classmethod
    @property
    def XEU(cls) -> IfcCurrencyEnum:
        ...
    
    @classmethod
    @property
    def ZAR(cls) -> IfcCurrencyEnum:
        ...
    
    @classmethod
    @property
    def ZWD(cls) -> IfcCurrencyEnum:
        ...
    
    @classmethod
    @property
    def NOK(cls) -> IfcCurrencyEnum:
        ...
    
    ...

class IfcCurtainWallTypeEnum:
    '''IfcCurtainWallTypeEnum'''
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcCurtainWallTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcCurtainWallTypeEnum:
        ...
    
    ...

class IfcDamperTypeEnum:
    '''IfcDamperTypeEnum'''
    
    @classmethod
    @property
    def CONTROLDAMPER(cls) -> IfcDamperTypeEnum:
        ...
    
    @classmethod
    @property
    def FIREDAMPER(cls) -> IfcDamperTypeEnum:
        ...
    
    @classmethod
    @property
    def SMOKEDAMPER(cls) -> IfcDamperTypeEnum:
        ...
    
    @classmethod
    @property
    def FIRESMOKEDAMPER(cls) -> IfcDamperTypeEnum:
        ...
    
    @classmethod
    @property
    def BACKDRAFTDAMPER(cls) -> IfcDamperTypeEnum:
        ...
    
    @classmethod
    @property
    def RELIEFDAMPER(cls) -> IfcDamperTypeEnum:
        ...
    
    @classmethod
    @property
    def BLASTDAMPER(cls) -> IfcDamperTypeEnum:
        ...
    
    @classmethod
    @property
    def GRAVITYDAMPER(cls) -> IfcDamperTypeEnum:
        ...
    
    @classmethod
    @property
    def GRAVITYRELIEFDAMPER(cls) -> IfcDamperTypeEnum:
        ...
    
    @classmethod
    @property
    def BALANCINGDAMPER(cls) -> IfcDamperTypeEnum:
        ...
    
    @classmethod
    @property
    def FUMEHOODEXHAUST(cls) -> IfcDamperTypeEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcDamperTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcDamperTypeEnum:
        ...
    
    ...

class IfcDataOriginEnum:
    '''IfcDataOriginEnum'''
    
    @classmethod
    @property
    def MEASURED(cls) -> IfcDataOriginEnum:
        ...
    
    @classmethod
    @property
    def PREDICTED(cls) -> IfcDataOriginEnum:
        ...
    
    @classmethod
    @property
    def SIMULATED(cls) -> IfcDataOriginEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcDataOriginEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcDataOriginEnum:
        ...
    
    ...

class IfcDerivedUnitEnum:
    '''IfcDerivedUnitEnum'''
    
    @classmethod
    @property
    def ANGULARVELOCITYUNIT(cls) -> IfcDerivedUnitEnum:
        ...
    
    @classmethod
    @property
    def COMPOUNDPLANEANGLEUNIT(cls) -> IfcDerivedUnitEnum:
        ...
    
    @classmethod
    @property
    def DYNAMICVISCOSITYUNIT(cls) -> IfcDerivedUnitEnum:
        ...
    
    @classmethod
    @property
    def HEATFLUXDENSITYUNIT(cls) -> IfcDerivedUnitEnum:
        ...
    
    @classmethod
    @property
    def INTEGERCOUNTRATEUNIT(cls) -> IfcDerivedUnitEnum:
        ...
    
    @classmethod
    @property
    def ISOTHERMALMOISTURECAPACITYUNIT(cls) -> IfcDerivedUnitEnum:
        ...
    
    @classmethod
    @property
    def KINEMATICVISCOSITYUNIT(cls) -> IfcDerivedUnitEnum:
        ...
    
    @classmethod
    @property
    def LINEARVELOCITYUNIT(cls) -> IfcDerivedUnitEnum:
        ...
    
    @classmethod
    @property
    def MASSDENSITYUNIT(cls) -> IfcDerivedUnitEnum:
        ...
    
    @classmethod
    @property
    def MASSFLOWRATEUNIT(cls) -> IfcDerivedUnitEnum:
        ...
    
    @classmethod
    @property
    def MOISTUREDIFFUSIVITYUNIT(cls) -> IfcDerivedUnitEnum:
        ...
    
    @classmethod
    @property
    def MOLECULARWEIGHTUNIT(cls) -> IfcDerivedUnitEnum:
        ...
    
    @classmethod
    @property
    def SPECIFICHEATCAPACITYUNIT(cls) -> IfcDerivedUnitEnum:
        ...
    
    @classmethod
    @property
    def THERMALADMITTANCEUNIT(cls) -> IfcDerivedUnitEnum:
        ...
    
    @classmethod
    @property
    def THERMALCONDUCTANCEUNIT(cls) -> IfcDerivedUnitEnum:
        ...
    
    @classmethod
    @property
    def THERMALRESISTANCEUNIT(cls) -> IfcDerivedUnitEnum:
        ...
    
    @classmethod
    @property
    def THERMALTRANSMITTANCEUNIT(cls) -> IfcDerivedUnitEnum:
        ...
    
    @classmethod
    @property
    def VAPORPERMEABILITYUNIT(cls) -> IfcDerivedUnitEnum:
        ...
    
    @classmethod
    @property
    def VOLUMETRICFLOWRATEUNIT(cls) -> IfcDerivedUnitEnum:
        ...
    
    @classmethod
    @property
    def ROTATIONALFREQUENCYUNIT(cls) -> IfcDerivedUnitEnum:
        ...
    
    @classmethod
    @property
    def TORQUEUNIT(cls) -> IfcDerivedUnitEnum:
        ...
    
    @classmethod
    @property
    def MOMENTOFINERTIAUNIT(cls) -> IfcDerivedUnitEnum:
        ...
    
    @classmethod
    @property
    def LINEARMOMENTUNIT(cls) -> IfcDerivedUnitEnum:
        ...
    
    @classmethod
    @property
    def LINEARFORCEUNIT(cls) -> IfcDerivedUnitEnum:
        ...
    
    @classmethod
    @property
    def PLANARFORCEUNIT(cls) -> IfcDerivedUnitEnum:
        ...
    
    @classmethod
    @property
    def MODULUSOFELASTICITYUNIT(cls) -> IfcDerivedUnitEnum:
        ...
    
    @classmethod
    @property
    def SHEARMODULUSUNIT(cls) -> IfcDerivedUnitEnum:
        ...
    
    @classmethod
    @property
    def LINEARSTIFFNESSUNIT(cls) -> IfcDerivedUnitEnum:
        ...
    
    @classmethod
    @property
    def ROTATIONALSTIFFNESSUNIT(cls) -> IfcDerivedUnitEnum:
        ...
    
    @classmethod
    @property
    def MODULUSOFSUBGRADEREACTIONUNIT(cls) -> IfcDerivedUnitEnum:
        ...
    
    @classmethod
    @property
    def ACCELERATIONUNIT(cls) -> IfcDerivedUnitEnum:
        ...
    
    @classmethod
    @property
    def CURVATUREUNIT(cls) -> IfcDerivedUnitEnum:
        ...
    
    @classmethod
    @property
    def HEATINGVALUEUNIT(cls) -> IfcDerivedUnitEnum:
        ...
    
    @classmethod
    @property
    def IONCONCENTRATIONUNIT(cls) -> IfcDerivedUnitEnum:
        ...
    
    @classmethod
    @property
    def LUMINOUSINTENSITYDISTRIBUTIONUNIT(cls) -> IfcDerivedUnitEnum:
        ...
    
    @classmethod
    @property
    def MASSPERLENGTHUNIT(cls) -> IfcDerivedUnitEnum:
        ...
    
    @classmethod
    @property
    def MODULUSOFLINEARSUBGRADEREACTIONUNIT(cls) -> IfcDerivedUnitEnum:
        ...
    
    @classmethod
    @property
    def MODULUSOFROTATIONALSUBGRADEREACTIONUNIT(cls) -> IfcDerivedUnitEnum:
        ...
    
    @classmethod
    @property
    def PHUNIT(cls) -> IfcDerivedUnitEnum:
        ...
    
    @classmethod
    @property
    def ROTATIONALMASSUNIT(cls) -> IfcDerivedUnitEnum:
        ...
    
    @classmethod
    @property
    def SECTIONAREAINTEGRALUNIT(cls) -> IfcDerivedUnitEnum:
        ...
    
    @classmethod
    @property
    def SECTIONMODULUSUNIT(cls) -> IfcDerivedUnitEnum:
        ...
    
    @classmethod
    @property
    def SOUNDPOWERUNIT(cls) -> IfcDerivedUnitEnum:
        ...
    
    @classmethod
    @property
    def SOUNDPRESSUREUNIT(cls) -> IfcDerivedUnitEnum:
        ...
    
    @classmethod
    @property
    def TEMPERATUREGRADIENTUNIT(cls) -> IfcDerivedUnitEnum:
        ...
    
    @classmethod
    @property
    def THERMALEXPANSIONCOEFFICIENTUNIT(cls) -> IfcDerivedUnitEnum:
        ...
    
    @classmethod
    @property
    def WARPINGCONSTANTUNIT(cls) -> IfcDerivedUnitEnum:
        ...
    
    @classmethod
    @property
    def WARPINGMOMENTUNIT(cls) -> IfcDerivedUnitEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcDerivedUnitEnum:
        ...
    
    ...

class IfcDimensionExtentUsage:
    '''IfcDimensionExtentUsage'''
    
    @classmethod
    @property
    def ORIGIN(cls) -> IfcDimensionExtentUsage:
        ...
    
    @classmethod
    @property
    def TARGET(cls) -> IfcDimensionExtentUsage:
        ...
    
    ...

class IfcDirectionSenseEnum:
    '''IfcDirectionSenseEnum'''
    
    @classmethod
    @property
    def POSITIVE(cls) -> IfcDirectionSenseEnum:
        ...
    
    @classmethod
    @property
    def NEGATIVE(cls) -> IfcDirectionSenseEnum:
        ...
    
    ...

class IfcDistributionChamberElementTypeEnum:
    '''IfcDistributionChamberElementTypeEnum'''
    
    @classmethod
    @property
    def FORMEDDUCT(cls) -> IfcDistributionChamberElementTypeEnum:
        ...
    
    @classmethod
    @property
    def INSPECTIONCHAMBER(cls) -> IfcDistributionChamberElementTypeEnum:
        ...
    
    @classmethod
    @property
    def INSPECTIONPIT(cls) -> IfcDistributionChamberElementTypeEnum:
        ...
    
    @classmethod
    @property
    def MANHOLE(cls) -> IfcDistributionChamberElementTypeEnum:
        ...
    
    @classmethod
    @property
    def METERCHAMBER(cls) -> IfcDistributionChamberElementTypeEnum:
        ...
    
    @classmethod
    @property
    def SUMP(cls) -> IfcDistributionChamberElementTypeEnum:
        ...
    
    @classmethod
    @property
    def TRENCH(cls) -> IfcDistributionChamberElementTypeEnum:
        ...
    
    @classmethod
    @property
    def VALVECHAMBER(cls) -> IfcDistributionChamberElementTypeEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcDistributionChamberElementTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcDistributionChamberElementTypeEnum:
        ...
    
    ...

class IfcDocumentConfidentialityEnum:
    '''IfcDocumentConfidentialityEnum'''
    
    @classmethod
    @property
    def PUBLIC(cls) -> IfcDocumentConfidentialityEnum:
        ...
    
    @classmethod
    @property
    def RESTRICTED(cls) -> IfcDocumentConfidentialityEnum:
        ...
    
    @classmethod
    @property
    def CONFIDENTIAL(cls) -> IfcDocumentConfidentialityEnum:
        ...
    
    @classmethod
    @property
    def PERSONAL(cls) -> IfcDocumentConfidentialityEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcDocumentConfidentialityEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcDocumentConfidentialityEnum:
        ...
    
    ...

class IfcDocumentStatusEnum:
    '''IfcDocumentStatusEnum'''
    
    @classmethod
    @property
    def DRAFT(cls) -> IfcDocumentStatusEnum:
        ...
    
    @classmethod
    @property
    def FINALDRAFT(cls) -> IfcDocumentStatusEnum:
        ...
    
    @classmethod
    @property
    def FINAL(cls) -> IfcDocumentStatusEnum:
        ...
    
    @classmethod
    @property
    def REVISION(cls) -> IfcDocumentStatusEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcDocumentStatusEnum:
        ...
    
    ...

class IfcDoorPanelOperationEnum:
    '''IfcDoorPanelOperationEnum'''
    
    @classmethod
    @property
    def SWINGING(cls) -> IfcDoorPanelOperationEnum:
        ...
    
    @classmethod
    @property
    def DOUBLE_ACTING(cls) -> IfcDoorPanelOperationEnum:
        ...
    
    @classmethod
    @property
    def SLIDING(cls) -> IfcDoorPanelOperationEnum:
        ...
    
    @classmethod
    @property
    def FOLDING(cls) -> IfcDoorPanelOperationEnum:
        ...
    
    @classmethod
    @property
    def REVOLVING(cls) -> IfcDoorPanelOperationEnum:
        ...
    
    @classmethod
    @property
    def ROLLINGUP(cls) -> IfcDoorPanelOperationEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcDoorPanelOperationEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcDoorPanelOperationEnum:
        ...
    
    ...

class IfcDoorPanelPositionEnum:
    '''IfcDoorPanelPositionEnum'''
    
    @classmethod
    @property
    def LEFT(cls) -> IfcDoorPanelPositionEnum:
        ...
    
    @classmethod
    @property
    def MIDDLE(cls) -> IfcDoorPanelPositionEnum:
        ...
    
    @classmethod
    @property
    def RIGHT(cls) -> IfcDoorPanelPositionEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcDoorPanelPositionEnum:
        ...
    
    ...

class IfcDoorStyleConstructionEnum:
    '''IfcDoorStyleConstructionEnum'''
    
    @classmethod
    @property
    def ALUMINIUM(cls) -> IfcDoorStyleConstructionEnum:
        ...
    
    @classmethod
    @property
    def HIGH_GRADE_STEEL(cls) -> IfcDoorStyleConstructionEnum:
        ...
    
    @classmethod
    @property
    def STEEL(cls) -> IfcDoorStyleConstructionEnum:
        ...
    
    @classmethod
    @property
    def WOOD(cls) -> IfcDoorStyleConstructionEnum:
        ...
    
    @classmethod
    @property
    def ALUMINIUM_WOOD(cls) -> IfcDoorStyleConstructionEnum:
        ...
    
    @classmethod
    @property
    def ALUMINIUM_PLASTIC(cls) -> IfcDoorStyleConstructionEnum:
        ...
    
    @classmethod
    @property
    def PLASTIC(cls) -> IfcDoorStyleConstructionEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcDoorStyleConstructionEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcDoorStyleConstructionEnum:
        ...
    
    ...

class IfcDoorStyleOperationEnum:
    '''IfcDoorStyleOperationEnum'''
    
    @classmethod
    @property
    def SINGLE_SWING_LEFT(cls) -> IfcDoorStyleOperationEnum:
        ...
    
    @classmethod
    @property
    def SINGLE_SWING_RIGHT(cls) -> IfcDoorStyleOperationEnum:
        ...
    
    @classmethod
    @property
    def DOUBLE_DOOR_SINGLE_SWING(cls) -> IfcDoorStyleOperationEnum:
        ...
    
    @classmethod
    @property
    def DOUBLE_DOOR_SINGLE_SWING_OPPOSITE_LEFT(cls) -> IfcDoorStyleOperationEnum:
        ...
    
    @classmethod
    @property
    def DOUBLE_DOOR_SINGLE_SWING_OPPOSITE_RIGHT(cls) -> IfcDoorStyleOperationEnum:
        ...
    
    @classmethod
    @property
    def DOUBLE_SWING_LEFT(cls) -> IfcDoorStyleOperationEnum:
        ...
    
    @classmethod
    @property
    def DOUBLE_SWING_RIGHT(cls) -> IfcDoorStyleOperationEnum:
        ...
    
    @classmethod
    @property
    def DOUBLE_DOOR_DOUBLE_SWING(cls) -> IfcDoorStyleOperationEnum:
        ...
    
    @classmethod
    @property
    def SLIDING_TO_LEFT(cls) -> IfcDoorStyleOperationEnum:
        ...
    
    @classmethod
    @property
    def SLIDING_TO_RIGHT(cls) -> IfcDoorStyleOperationEnum:
        ...
    
    @classmethod
    @property
    def DOUBLE_DOOR_SLIDING(cls) -> IfcDoorStyleOperationEnum:
        ...
    
    @classmethod
    @property
    def FOLDING_TO_LEFT(cls) -> IfcDoorStyleOperationEnum:
        ...
    
    @classmethod
    @property
    def FOLDING_TO_RIGHT(cls) -> IfcDoorStyleOperationEnum:
        ...
    
    @classmethod
    @property
    def DOUBLE_DOOR_FOLDING(cls) -> IfcDoorStyleOperationEnum:
        ...
    
    @classmethod
    @property
    def REVOLVING(cls) -> IfcDoorStyleOperationEnum:
        ...
    
    @classmethod
    @property
    def ROLLINGUP(cls) -> IfcDoorStyleOperationEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcDoorStyleOperationEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcDoorStyleOperationEnum:
        ...
    
    ...

class IfcDuctFittingTypeEnum:
    '''IfcDuctFittingTypeEnum'''
    
    @classmethod
    @property
    def BEND(cls) -> IfcDuctFittingTypeEnum:
        ...
    
    @classmethod
    @property
    def CONNECTOR(cls) -> IfcDuctFittingTypeEnum:
        ...
    
    @classmethod
    @property
    def ENTRY(cls) -> IfcDuctFittingTypeEnum:
        ...
    
    @classmethod
    @property
    def EXIT(cls) -> IfcDuctFittingTypeEnum:
        ...
    
    @classmethod
    @property
    def JUNCTION(cls) -> IfcDuctFittingTypeEnum:
        ...
    
    @classmethod
    @property
    def OBSTRUCTION(cls) -> IfcDuctFittingTypeEnum:
        ...
    
    @classmethod
    @property
    def TRANSITION(cls) -> IfcDuctFittingTypeEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcDuctFittingTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcDuctFittingTypeEnum:
        ...
    
    ...

class IfcDuctSegmentTypeEnum:
    '''IfcDuctSegmentTypeEnum'''
    
    @classmethod
    @property
    def RIGIDSEGMENT(cls) -> IfcDuctSegmentTypeEnum:
        ...
    
    @classmethod
    @property
    def FLEXIBLESEGMENT(cls) -> IfcDuctSegmentTypeEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcDuctSegmentTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcDuctSegmentTypeEnum:
        ...
    
    ...

class IfcDuctSilencerTypeEnum:
    '''IfcDuctSilencerTypeEnum'''
    
    @classmethod
    @property
    def FLATOVAL(cls) -> IfcDuctSilencerTypeEnum:
        ...
    
    @classmethod
    @property
    def RECTANGULAR(cls) -> IfcDuctSilencerTypeEnum:
        ...
    
    @classmethod
    @property
    def ROUND(cls) -> IfcDuctSilencerTypeEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcDuctSilencerTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcDuctSilencerTypeEnum:
        ...
    
    ...

class IfcElectricApplianceTypeEnum:
    '''IfcElectricApplianceTypeEnum'''
    
    @classmethod
    @property
    def COMPUTER(cls) -> IfcElectricApplianceTypeEnum:
        ...
    
    @classmethod
    @property
    def DIRECTWATERHEATER(cls) -> IfcElectricApplianceTypeEnum:
        ...
    
    @classmethod
    @property
    def DISHWASHER(cls) -> IfcElectricApplianceTypeEnum:
        ...
    
    @classmethod
    @property
    def ELECTRICCOOKER(cls) -> IfcElectricApplianceTypeEnum:
        ...
    
    @classmethod
    @property
    def ELECTRICHEATER(cls) -> IfcElectricApplianceTypeEnum:
        ...
    
    @classmethod
    @property
    def FACSIMILE(cls) -> IfcElectricApplianceTypeEnum:
        ...
    
    @classmethod
    @property
    def FREESTANDINGFAN(cls) -> IfcElectricApplianceTypeEnum:
        ...
    
    @classmethod
    @property
    def FREEZER(cls) -> IfcElectricApplianceTypeEnum:
        ...
    
    @classmethod
    @property
    def FRIDGE_FREEZER(cls) -> IfcElectricApplianceTypeEnum:
        ...
    
    @classmethod
    @property
    def HANDDRYER(cls) -> IfcElectricApplianceTypeEnum:
        ...
    
    @classmethod
    @property
    def INDIRECTWATERHEATER(cls) -> IfcElectricApplianceTypeEnum:
        ...
    
    @classmethod
    @property
    def MICROWAVE(cls) -> IfcElectricApplianceTypeEnum:
        ...
    
    @classmethod
    @property
    def PHOTOCOPIER(cls) -> IfcElectricApplianceTypeEnum:
        ...
    
    @classmethod
    @property
    def PRINTER(cls) -> IfcElectricApplianceTypeEnum:
        ...
    
    @classmethod
    @property
    def REFRIGERATOR(cls) -> IfcElectricApplianceTypeEnum:
        ...
    
    @classmethod
    @property
    def RADIANTHEATER(cls) -> IfcElectricApplianceTypeEnum:
        ...
    
    @classmethod
    @property
    def SCANNER(cls) -> IfcElectricApplianceTypeEnum:
        ...
    
    @classmethod
    @property
    def TELEPHONE(cls) -> IfcElectricApplianceTypeEnum:
        ...
    
    @classmethod
    @property
    def TUMBLEDRYER(cls) -> IfcElectricApplianceTypeEnum:
        ...
    
    @classmethod
    @property
    def TV(cls) -> IfcElectricApplianceTypeEnum:
        ...
    
    @classmethod
    @property
    def VENDINGMACHINE(cls) -> IfcElectricApplianceTypeEnum:
        ...
    
    @classmethod
    @property
    def WASHINGMACHINE(cls) -> IfcElectricApplianceTypeEnum:
        ...
    
    @classmethod
    @property
    def WATERHEATER(cls) -> IfcElectricApplianceTypeEnum:
        ...
    
    @classmethod
    @property
    def WATERCOOLER(cls) -> IfcElectricApplianceTypeEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcElectricApplianceTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcElectricApplianceTypeEnum:
        ...
    
    ...

class IfcElectricCurrentEnum:
    '''IfcElectricCurrentEnum'''
    
    @classmethod
    @property
    def ALTERNATING(cls) -> IfcElectricCurrentEnum:
        ...
    
    @classmethod
    @property
    def DIRECT(cls) -> IfcElectricCurrentEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcElectricCurrentEnum:
        ...
    
    ...

class IfcElectricDistributionPointFunctionEnum:
    '''IfcElectricDistributionPointFunctionEnum'''
    
    @classmethod
    @property
    def ALARMPANEL(cls) -> IfcElectricDistributionPointFunctionEnum:
        ...
    
    @classmethod
    @property
    def CONSUMERUNIT(cls) -> IfcElectricDistributionPointFunctionEnum:
        ...
    
    @classmethod
    @property
    def CONTROLPANEL(cls) -> IfcElectricDistributionPointFunctionEnum:
        ...
    
    @classmethod
    @property
    def DISTRIBUTIONBOARD(cls) -> IfcElectricDistributionPointFunctionEnum:
        ...
    
    @classmethod
    @property
    def GASDETECTORPANEL(cls) -> IfcElectricDistributionPointFunctionEnum:
        ...
    
    @classmethod
    @property
    def INDICATORPANEL(cls) -> IfcElectricDistributionPointFunctionEnum:
        ...
    
    @classmethod
    @property
    def MIMICPANEL(cls) -> IfcElectricDistributionPointFunctionEnum:
        ...
    
    @classmethod
    @property
    def MOTORCONTROLCENTRE(cls) -> IfcElectricDistributionPointFunctionEnum:
        ...
    
    @classmethod
    @property
    def SWITCHBOARD(cls) -> IfcElectricDistributionPointFunctionEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcElectricDistributionPointFunctionEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcElectricDistributionPointFunctionEnum:
        ...
    
    ...

class IfcElectricFlowStorageDeviceTypeEnum:
    '''IfcElectricFlowStorageDeviceTypeEnum'''
    
    @classmethod
    @property
    def BATTERY(cls) -> IfcElectricFlowStorageDeviceTypeEnum:
        ...
    
    @classmethod
    @property
    def CAPACITORBANK(cls) -> IfcElectricFlowStorageDeviceTypeEnum:
        ...
    
    @classmethod
    @property
    def HARMONICFILTER(cls) -> IfcElectricFlowStorageDeviceTypeEnum:
        ...
    
    @classmethod
    @property
    def INDUCTORBANK(cls) -> IfcElectricFlowStorageDeviceTypeEnum:
        ...
    
    @classmethod
    @property
    def UPS(cls) -> IfcElectricFlowStorageDeviceTypeEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcElectricFlowStorageDeviceTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcElectricFlowStorageDeviceTypeEnum:
        ...
    
    ...

class IfcElectricGeneratorTypeEnum:
    '''IfcElectricGeneratorTypeEnum'''
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcElectricGeneratorTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcElectricGeneratorTypeEnum:
        ...
    
    ...

class IfcElectricHeaterTypeEnum:
    '''IfcElectricHeaterTypeEnum'''
    
    @classmethod
    @property
    def ELECTRICPOINTHEATER(cls) -> IfcElectricHeaterTypeEnum:
        ...
    
    @classmethod
    @property
    def ELECTRICCABLEHEATER(cls) -> IfcElectricHeaterTypeEnum:
        ...
    
    @classmethod
    @property
    def ELECTRICMATHEATER(cls) -> IfcElectricHeaterTypeEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcElectricHeaterTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcElectricHeaterTypeEnum:
        ...
    
    ...

class IfcElectricMotorTypeEnum:
    '''IfcElectricMotorTypeEnum'''
    
    @classmethod
    @property
    def DC(cls) -> IfcElectricMotorTypeEnum:
        ...
    
    @classmethod
    @property
    def INDUCTION(cls) -> IfcElectricMotorTypeEnum:
        ...
    
    @classmethod
    @property
    def POLYPHASE(cls) -> IfcElectricMotorTypeEnum:
        ...
    
    @classmethod
    @property
    def RELUCTANCESYNCHRONOUS(cls) -> IfcElectricMotorTypeEnum:
        ...
    
    @classmethod
    @property
    def SYNCHRONOUS(cls) -> IfcElectricMotorTypeEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcElectricMotorTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcElectricMotorTypeEnum:
        ...
    
    ...

class IfcElectricTimeControlTypeEnum:
    '''IfcElectricTimeControlTypeEnum'''
    
    @classmethod
    @property
    def TIMECLOCK(cls) -> IfcElectricTimeControlTypeEnum:
        ...
    
    @classmethod
    @property
    def TIMEDELAY(cls) -> IfcElectricTimeControlTypeEnum:
        ...
    
    @classmethod
    @property
    def RELAY(cls) -> IfcElectricTimeControlTypeEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcElectricTimeControlTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcElectricTimeControlTypeEnum:
        ...
    
    ...

class IfcElementAssemblyTypeEnum:
    '''IfcElementAssemblyTypeEnum'''
    
    @classmethod
    @property
    def ACCESSORY_ASSEMBLY(cls) -> IfcElementAssemblyTypeEnum:
        ...
    
    @classmethod
    @property
    def ARCH(cls) -> IfcElementAssemblyTypeEnum:
        ...
    
    @classmethod
    @property
    def BEAM_GRID(cls) -> IfcElementAssemblyTypeEnum:
        ...
    
    @classmethod
    @property
    def BRACED_FRAME(cls) -> IfcElementAssemblyTypeEnum:
        ...
    
    @classmethod
    @property
    def GIRDER(cls) -> IfcElementAssemblyTypeEnum:
        ...
    
    @classmethod
    @property
    def REINFORCEMENT_UNIT(cls) -> IfcElementAssemblyTypeEnum:
        ...
    
    @classmethod
    @property
    def RIGID_FRAME(cls) -> IfcElementAssemblyTypeEnum:
        ...
    
    @classmethod
    @property
    def SLAB_FIELD(cls) -> IfcElementAssemblyTypeEnum:
        ...
    
    @classmethod
    @property
    def TRUSS(cls) -> IfcElementAssemblyTypeEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcElementAssemblyTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcElementAssemblyTypeEnum:
        ...
    
    ...

class IfcElementCompositionEnum:
    '''IfcElementCompositionEnum'''
    
    @classmethod
    @property
    def COMPLEX(cls) -> IfcElementCompositionEnum:
        ...
    
    @classmethod
    @property
    def ELEMENT(cls) -> IfcElementCompositionEnum:
        ...
    
    @classmethod
    @property
    def PARTIAL(cls) -> IfcElementCompositionEnum:
        ...
    
    ...

class IfcEnergySequenceEnum:
    '''IfcEnergySequenceEnum'''
    
    @classmethod
    @property
    def PRIMARY(cls) -> IfcEnergySequenceEnum:
        ...
    
    @classmethod
    @property
    def SECONDARY(cls) -> IfcEnergySequenceEnum:
        ...
    
    @classmethod
    @property
    def TERTIARY(cls) -> IfcEnergySequenceEnum:
        ...
    
    @classmethod
    @property
    def AUXILIARY(cls) -> IfcEnergySequenceEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcEnergySequenceEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcEnergySequenceEnum:
        ...
    
    ...

class IfcEnvironmentalImpactCategoryEnum:
    '''IfcEnvironmentalImpactCategoryEnum'''
    
    @classmethod
    @property
    def COMBINEDVALUE(cls) -> IfcEnvironmentalImpactCategoryEnum:
        ...
    
    @classmethod
    @property
    def DISPOSAL(cls) -> IfcEnvironmentalImpactCategoryEnum:
        ...
    
    @classmethod
    @property
    def EXTRACTION(cls) -> IfcEnvironmentalImpactCategoryEnum:
        ...
    
    @classmethod
    @property
    def INSTALLATION(cls) -> IfcEnvironmentalImpactCategoryEnum:
        ...
    
    @classmethod
    @property
    def MANUFACTURE(cls) -> IfcEnvironmentalImpactCategoryEnum:
        ...
    
    @classmethod
    @property
    def TRANSPORTATION(cls) -> IfcEnvironmentalImpactCategoryEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcEnvironmentalImpactCategoryEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcEnvironmentalImpactCategoryEnum:
        ...
    
    ...

class IfcEvaporativeCoolerTypeEnum:
    '''IfcEvaporativeCoolerTypeEnum'''
    
    @classmethod
    @property
    def DIRECTEVAPORATIVERANDOMMEDIAAIRCOOLER(cls) -> IfcEvaporativeCoolerTypeEnum:
        ...
    
    @classmethod
    @property
    def DIRECTEVAPORATIVERIGIDMEDIAAIRCOOLER(cls) -> IfcEvaporativeCoolerTypeEnum:
        ...
    
    @classmethod
    @property
    def DIRECTEVAPORATIVESLINGERSPACKAGEDAIRCOOLER(cls) -> IfcEvaporativeCoolerTypeEnum:
        ...
    
    @classmethod
    @property
    def DIRECTEVAPORATIVEPACKAGEDROTARYAIRCOOLER(cls) -> IfcEvaporativeCoolerTypeEnum:
        ...
    
    @classmethod
    @property
    def DIRECTEVAPORATIVEAIRWASHER(cls) -> IfcEvaporativeCoolerTypeEnum:
        ...
    
    @classmethod
    @property
    def INDIRECTEVAPORATIVEPACKAGEAIRCOOLER(cls) -> IfcEvaporativeCoolerTypeEnum:
        ...
    
    @classmethod
    @property
    def INDIRECTEVAPORATIVEWETCOIL(cls) -> IfcEvaporativeCoolerTypeEnum:
        ...
    
    @classmethod
    @property
    def INDIRECTEVAPORATIVECOOLINGTOWERORCOILCOOLER(cls) -> IfcEvaporativeCoolerTypeEnum:
        ...
    
    @classmethod
    @property
    def INDIRECTDIRECTCOMBINATION(cls) -> IfcEvaporativeCoolerTypeEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcEvaporativeCoolerTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcEvaporativeCoolerTypeEnum:
        ...
    
    ...

class IfcEvaporatorTypeEnum:
    '''IfcEvaporatorTypeEnum'''
    
    @classmethod
    @property
    def DIRECTEXPANSIONSHELLANDTUBE(cls) -> IfcEvaporatorTypeEnum:
        ...
    
    @classmethod
    @property
    def DIRECTEXPANSIONTUBEINTUBE(cls) -> IfcEvaporatorTypeEnum:
        ...
    
    @classmethod
    @property
    def DIRECTEXPANSIONBRAZEDPLATE(cls) -> IfcEvaporatorTypeEnum:
        ...
    
    @classmethod
    @property
    def FLOODEDSHELLANDTUBE(cls) -> IfcEvaporatorTypeEnum:
        ...
    
    @classmethod
    @property
    def SHELLANDCOIL(cls) -> IfcEvaporatorTypeEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcEvaporatorTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcEvaporatorTypeEnum:
        ...
    
    ...

class IfcFanTypeEnum:
    '''IfcFanTypeEnum'''
    
    @classmethod
    @property
    def CENTRIFUGALFORWARDCURVED(cls) -> IfcFanTypeEnum:
        ...
    
    @classmethod
    @property
    def CENTRIFUGALRADIAL(cls) -> IfcFanTypeEnum:
        ...
    
    @classmethod
    @property
    def CENTRIFUGALBACKWARDINCLINEDCURVED(cls) -> IfcFanTypeEnum:
        ...
    
    @classmethod
    @property
    def CENTRIFUGALAIRFOIL(cls) -> IfcFanTypeEnum:
        ...
    
    @classmethod
    @property
    def TUBEAXIAL(cls) -> IfcFanTypeEnum:
        ...
    
    @classmethod
    @property
    def VANEAXIAL(cls) -> IfcFanTypeEnum:
        ...
    
    @classmethod
    @property
    def PROPELLORAXIAL(cls) -> IfcFanTypeEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcFanTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcFanTypeEnum:
        ...
    
    ...

class IfcFilterTypeEnum:
    '''IfcFilterTypeEnum'''
    
    @classmethod
    @property
    def AIRPARTICLEFILTER(cls) -> IfcFilterTypeEnum:
        ...
    
    @classmethod
    @property
    def ODORFILTER(cls) -> IfcFilterTypeEnum:
        ...
    
    @classmethod
    @property
    def OILFILTER(cls) -> IfcFilterTypeEnum:
        ...
    
    @classmethod
    @property
    def STRAINER(cls) -> IfcFilterTypeEnum:
        ...
    
    @classmethod
    @property
    def WATERFILTER(cls) -> IfcFilterTypeEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcFilterTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcFilterTypeEnum:
        ...
    
    ...

class IfcFireSuppressionTerminalTypeEnum:
    '''IfcFireSuppressionTerminalTypeEnum'''
    
    @classmethod
    @property
    def BREECHINGINLET(cls) -> IfcFireSuppressionTerminalTypeEnum:
        ...
    
    @classmethod
    @property
    def FIREHYDRANT(cls) -> IfcFireSuppressionTerminalTypeEnum:
        ...
    
    @classmethod
    @property
    def HOSEREEL(cls) -> IfcFireSuppressionTerminalTypeEnum:
        ...
    
    @classmethod
    @property
    def SPRINKLER(cls) -> IfcFireSuppressionTerminalTypeEnum:
        ...
    
    @classmethod
    @property
    def SPRINKLERDEFLECTOR(cls) -> IfcFireSuppressionTerminalTypeEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcFireSuppressionTerminalTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcFireSuppressionTerminalTypeEnum:
        ...
    
    ...

class IfcFlowDirectionEnum:
    '''IfcFlowDirectionEnum'''
    
    @classmethod
    @property
    def SOURCE(cls) -> IfcFlowDirectionEnum:
        ...
    
    @classmethod
    @property
    def SINK(cls) -> IfcFlowDirectionEnum:
        ...
    
    @classmethod
    @property
    def SOURCEANDSINK(cls) -> IfcFlowDirectionEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcFlowDirectionEnum:
        ...
    
    ...

class IfcFlowInstrumentTypeEnum:
    '''IfcFlowInstrumentTypeEnum'''
    
    @classmethod
    @property
    def PRESSUREGAUGE(cls) -> IfcFlowInstrumentTypeEnum:
        ...
    
    @classmethod
    @property
    def THERMOMETER(cls) -> IfcFlowInstrumentTypeEnum:
        ...
    
    @classmethod
    @property
    def AMMETER(cls) -> IfcFlowInstrumentTypeEnum:
        ...
    
    @classmethod
    @property
    def FREQUENCYMETER(cls) -> IfcFlowInstrumentTypeEnum:
        ...
    
    @classmethod
    @property
    def POWERFACTORMETER(cls) -> IfcFlowInstrumentTypeEnum:
        ...
    
    @classmethod
    @property
    def PHASEANGLEMETER(cls) -> IfcFlowInstrumentTypeEnum:
        ...
    
    @classmethod
    @property
    def VOLTMETER_PEAK(cls) -> IfcFlowInstrumentTypeEnum:
        ...
    
    @classmethod
    @property
    def VOLTMETER_RMS(cls) -> IfcFlowInstrumentTypeEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcFlowInstrumentTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcFlowInstrumentTypeEnum:
        ...
    
    ...

class IfcFlowMeterTypeEnum:
    '''IfcFlowMeterTypeEnum'''
    
    @classmethod
    @property
    def ELECTRICMETER(cls) -> IfcFlowMeterTypeEnum:
        ...
    
    @classmethod
    @property
    def ENERGYMETER(cls) -> IfcFlowMeterTypeEnum:
        ...
    
    @classmethod
    @property
    def FLOWMETER(cls) -> IfcFlowMeterTypeEnum:
        ...
    
    @classmethod
    @property
    def GASMETER(cls) -> IfcFlowMeterTypeEnum:
        ...
    
    @classmethod
    @property
    def OILMETER(cls) -> IfcFlowMeterTypeEnum:
        ...
    
    @classmethod
    @property
    def WATERMETER(cls) -> IfcFlowMeterTypeEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcFlowMeterTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcFlowMeterTypeEnum:
        ...
    
    ...

class IfcFootingTypeEnum:
    '''IfcFootingTypeEnum'''
    
    @classmethod
    @property
    def FOOTING_BEAM(cls) -> IfcFootingTypeEnum:
        ...
    
    @classmethod
    @property
    def PAD_FOOTING(cls) -> IfcFootingTypeEnum:
        ...
    
    @classmethod
    @property
    def PILE_CAP(cls) -> IfcFootingTypeEnum:
        ...
    
    @classmethod
    @property
    def STRIP_FOOTING(cls) -> IfcFootingTypeEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcFootingTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcFootingTypeEnum:
        ...
    
    ...

class IfcGasTerminalTypeEnum:
    '''IfcGasTerminalTypeEnum'''
    
    @classmethod
    @property
    def GASAPPLIANCE(cls) -> IfcGasTerminalTypeEnum:
        ...
    
    @classmethod
    @property
    def GASBOOSTER(cls) -> IfcGasTerminalTypeEnum:
        ...
    
    @classmethod
    @property
    def GASBURNER(cls) -> IfcGasTerminalTypeEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcGasTerminalTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcGasTerminalTypeEnum:
        ...
    
    ...

class IfcGeometricProjectionEnum:
    '''IfcGeometricProjectionEnum'''
    
    @classmethod
    @property
    def GRAPH_VIEW(cls) -> IfcGeometricProjectionEnum:
        ...
    
    @classmethod
    @property
    def SKETCH_VIEW(cls) -> IfcGeometricProjectionEnum:
        ...
    
    @classmethod
    @property
    def MODEL_VIEW(cls) -> IfcGeometricProjectionEnum:
        ...
    
    @classmethod
    @property
    def PLAN_VIEW(cls) -> IfcGeometricProjectionEnum:
        ...
    
    @classmethod
    @property
    def REFLECTED_PLAN_VIEW(cls) -> IfcGeometricProjectionEnum:
        ...
    
    @classmethod
    @property
    def SECTION_VIEW(cls) -> IfcGeometricProjectionEnum:
        ...
    
    @classmethod
    @property
    def ELEVATION_VIEW(cls) -> IfcGeometricProjectionEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcGeometricProjectionEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcGeometricProjectionEnum:
        ...
    
    ...

class IfcGlobalOrLocalEnum:
    '''IfcGlobalOrLocalEnum'''
    
    @classmethod
    @property
    def GLOBAL_COORDS(cls) -> IfcGlobalOrLocalEnum:
        ...
    
    @classmethod
    @property
    def LOCAL_COORDS(cls) -> IfcGlobalOrLocalEnum:
        ...
    
    ...

class IfcHeatExchangerTypeEnum:
    '''IfcHeatExchangerTypeEnum'''
    
    @classmethod
    @property
    def PLATE(cls) -> IfcHeatExchangerTypeEnum:
        ...
    
    @classmethod
    @property
    def SHELLANDTUBE(cls) -> IfcHeatExchangerTypeEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcHeatExchangerTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcHeatExchangerTypeEnum:
        ...
    
    ...

class IfcHumidifierTypeEnum:
    '''IfcHumidifierTypeEnum'''
    
    @classmethod
    @property
    def STEAMINJECTION(cls) -> IfcHumidifierTypeEnum:
        ...
    
    @classmethod
    @property
    def ADIABATICAIRWASHER(cls) -> IfcHumidifierTypeEnum:
        ...
    
    @classmethod
    @property
    def ADIABATICPAN(cls) -> IfcHumidifierTypeEnum:
        ...
    
    @classmethod
    @property
    def ADIABATICWETTEDELEMENT(cls) -> IfcHumidifierTypeEnum:
        ...
    
    @classmethod
    @property
    def ADIABATICATOMIZING(cls) -> IfcHumidifierTypeEnum:
        ...
    
    @classmethod
    @property
    def ADIABATICULTRASONIC(cls) -> IfcHumidifierTypeEnum:
        ...
    
    @classmethod
    @property
    def ADIABATICRIGIDMEDIA(cls) -> IfcHumidifierTypeEnum:
        ...
    
    @classmethod
    @property
    def ADIABATICCOMPRESSEDAIRNOZZLE(cls) -> IfcHumidifierTypeEnum:
        ...
    
    @classmethod
    @property
    def ASSISTEDELECTRIC(cls) -> IfcHumidifierTypeEnum:
        ...
    
    @classmethod
    @property
    def ASSISTEDNATURALGAS(cls) -> IfcHumidifierTypeEnum:
        ...
    
    @classmethod
    @property
    def ASSISTEDPROPANE(cls) -> IfcHumidifierTypeEnum:
        ...
    
    @classmethod
    @property
    def ASSISTEDBUTANE(cls) -> IfcHumidifierTypeEnum:
        ...
    
    @classmethod
    @property
    def ASSISTEDSTEAM(cls) -> IfcHumidifierTypeEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcHumidifierTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcHumidifierTypeEnum:
        ...
    
    ...

class IfcInternalOrExternalEnum:
    '''IfcInternalOrExternalEnum'''
    
    @classmethod
    @property
    def INTERNAL(cls) -> IfcInternalOrExternalEnum:
        ...
    
    @classmethod
    @property
    def EXTERNAL(cls) -> IfcInternalOrExternalEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcInternalOrExternalEnum:
        ...
    
    ...

class IfcInventoryTypeEnum:
    '''IfcInventoryTypeEnum'''
    
    @classmethod
    @property
    def ASSETINVENTORY(cls) -> IfcInventoryTypeEnum:
        ...
    
    @classmethod
    @property
    def SPACEINVENTORY(cls) -> IfcInventoryTypeEnum:
        ...
    
    @classmethod
    @property
    def FURNITUREINVENTORY(cls) -> IfcInventoryTypeEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcInventoryTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcInventoryTypeEnum:
        ...
    
    ...

class IfcJunctionBoxTypeEnum:
    '''IfcJunctionBoxTypeEnum'''
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcJunctionBoxTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcJunctionBoxTypeEnum:
        ...
    
    ...

class IfcLampTypeEnum:
    '''IfcLampTypeEnum'''
    
    @classmethod
    @property
    def COMPACTFLUORESCENT(cls) -> IfcLampTypeEnum:
        ...
    
    @classmethod
    @property
    def FLUORESCENT(cls) -> IfcLampTypeEnum:
        ...
    
    @classmethod
    @property
    def HIGHPRESSUREMERCURY(cls) -> IfcLampTypeEnum:
        ...
    
    @classmethod
    @property
    def HIGHPRESSURESODIUM(cls) -> IfcLampTypeEnum:
        ...
    
    @classmethod
    @property
    def METALHALIDE(cls) -> IfcLampTypeEnum:
        ...
    
    @classmethod
    @property
    def TUNGSTENFILAMENT(cls) -> IfcLampTypeEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcLampTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcLampTypeEnum:
        ...
    
    ...

class IfcLayerSetDirectionEnum:
    '''IfcLayerSetDirectionEnum'''
    
    @classmethod
    @property
    def AXIS1(cls) -> IfcLayerSetDirectionEnum:
        ...
    
    @classmethod
    @property
    def AXIS2(cls) -> IfcLayerSetDirectionEnum:
        ...
    
    @classmethod
    @property
    def AXIS3(cls) -> IfcLayerSetDirectionEnum:
        ...
    
    ...

class IfcLightDistributionCurveEnum:
    '''IfcLightDistributionCurveEnum'''
    
    @classmethod
    @property
    def TYPE_A(cls) -> IfcLightDistributionCurveEnum:
        ...
    
    @classmethod
    @property
    def TYPE_B(cls) -> IfcLightDistributionCurveEnum:
        ...
    
    @classmethod
    @property
    def TYPE_C(cls) -> IfcLightDistributionCurveEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcLightDistributionCurveEnum:
        ...
    
    ...

class IfcLightEmissionSourceEnum:
    '''IfcLightEmissionSourceEnum'''
    
    @classmethod
    @property
    def COMPACTFLUORESCENT(cls) -> IfcLightEmissionSourceEnum:
        ...
    
    @classmethod
    @property
    def FLUORESCENT(cls) -> IfcLightEmissionSourceEnum:
        ...
    
    @classmethod
    @property
    def HIGHPRESSUREMERCURY(cls) -> IfcLightEmissionSourceEnum:
        ...
    
    @classmethod
    @property
    def HIGHPRESSURESODIUM(cls) -> IfcLightEmissionSourceEnum:
        ...
    
    @classmethod
    @property
    def LIGHTEMITTINGDIODE(cls) -> IfcLightEmissionSourceEnum:
        ...
    
    @classmethod
    @property
    def LOWPRESSURESODIUM(cls) -> IfcLightEmissionSourceEnum:
        ...
    
    @classmethod
    @property
    def LOWVOLTAGEHALOGEN(cls) -> IfcLightEmissionSourceEnum:
        ...
    
    @classmethod
    @property
    def MAINVOLTAGEHALOGEN(cls) -> IfcLightEmissionSourceEnum:
        ...
    
    @classmethod
    @property
    def METALHALIDE(cls) -> IfcLightEmissionSourceEnum:
        ...
    
    @classmethod
    @property
    def TUNGSTENFILAMENT(cls) -> IfcLightEmissionSourceEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcLightEmissionSourceEnum:
        ...
    
    ...

class IfcLightFixtureTypeEnum:
    '''IfcLightFixtureTypeEnum'''
    
    @classmethod
    @property
    def POINTSOURCE(cls) -> IfcLightFixtureTypeEnum:
        ...
    
    @classmethod
    @property
    def DIRECTIONSOURCE(cls) -> IfcLightFixtureTypeEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcLightFixtureTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcLightFixtureTypeEnum:
        ...
    
    ...

class IfcLoadGroupTypeEnum:
    '''IfcLoadGroupTypeEnum'''
    
    @classmethod
    @property
    def LOAD_GROUP(cls) -> IfcLoadGroupTypeEnum:
        ...
    
    @classmethod
    @property
    def LOAD_CASE(cls) -> IfcLoadGroupTypeEnum:
        ...
    
    @classmethod
    @property
    def LOAD_COMBINATION_GROUP(cls) -> IfcLoadGroupTypeEnum:
        ...
    
    @classmethod
    @property
    def LOAD_COMBINATION(cls) -> IfcLoadGroupTypeEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcLoadGroupTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcLoadGroupTypeEnum:
        ...
    
    ...

class IfcLogicalOperatorEnum:
    '''IfcLogicalOperatorEnum'''
    
    @classmethod
    @property
    def LOGICALAND(cls) -> IfcLogicalOperatorEnum:
        ...
    
    @classmethod
    @property
    def LOGICALOR(cls) -> IfcLogicalOperatorEnum:
        ...
    
    ...

class IfcMemberTypeEnum:
    '''IfcMemberTypeEnum'''
    
    @classmethod
    @property
    def BRACE(cls) -> IfcMemberTypeEnum:
        ...
    
    @classmethod
    @property
    def CHORD(cls) -> IfcMemberTypeEnum:
        ...
    
    @classmethod
    @property
    def COLLAR(cls) -> IfcMemberTypeEnum:
        ...
    
    @classmethod
    @property
    def MEMBER(cls) -> IfcMemberTypeEnum:
        ...
    
    @classmethod
    @property
    def MULLION(cls) -> IfcMemberTypeEnum:
        ...
    
    @classmethod
    @property
    def PLATE(cls) -> IfcMemberTypeEnum:
        ...
    
    @classmethod
    @property
    def POST(cls) -> IfcMemberTypeEnum:
        ...
    
    @classmethod
    @property
    def PURLIN(cls) -> IfcMemberTypeEnum:
        ...
    
    @classmethod
    @property
    def RAFTER(cls) -> IfcMemberTypeEnum:
        ...
    
    @classmethod
    @property
    def STRINGER(cls) -> IfcMemberTypeEnum:
        ...
    
    @classmethod
    @property
    def STRUT(cls) -> IfcMemberTypeEnum:
        ...
    
    @classmethod
    @property
    def STUD(cls) -> IfcMemberTypeEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcMemberTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcMemberTypeEnum:
        ...
    
    ...

class IfcMotorConnectionTypeEnum:
    '''IfcMotorConnectionTypeEnum'''
    
    @classmethod
    @property
    def BELTDRIVE(cls) -> IfcMotorConnectionTypeEnum:
        ...
    
    @classmethod
    @property
    def COUPLING(cls) -> IfcMotorConnectionTypeEnum:
        ...
    
    @classmethod
    @property
    def DIRECTDRIVE(cls) -> IfcMotorConnectionTypeEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcMotorConnectionTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcMotorConnectionTypeEnum:
        ...
    
    ...

class IfcNullStyle:
    '''IfcNullStyle'''
    
    @classmethod
    @property
    def NULL(cls) -> IfcNullStyle:
        ...
    
    ...

class IfcObjectTypeEnum:
    '''IfcObjectTypeEnum'''
    
    @classmethod
    @property
    def PRODUCT(cls) -> IfcObjectTypeEnum:
        ...
    
    @classmethod
    @property
    def PROCESS(cls) -> IfcObjectTypeEnum:
        ...
    
    @classmethod
    @property
    def CONTROL(cls) -> IfcObjectTypeEnum:
        ...
    
    @classmethod
    @property
    def RESOURCE(cls) -> IfcObjectTypeEnum:
        ...
    
    @classmethod
    @property
    def ACTOR(cls) -> IfcObjectTypeEnum:
        ...
    
    @classmethod
    @property
    def GROUP(cls) -> IfcObjectTypeEnum:
        ...
    
    @classmethod
    @property
    def PROJECT(cls) -> IfcObjectTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcObjectTypeEnum:
        ...
    
    ...

class IfcObjectiveEnum:
    '''IfcObjectiveEnum'''
    
    @classmethod
    @property
    def CODECOMPLIANCE(cls) -> IfcObjectiveEnum:
        ...
    
    @classmethod
    @property
    def DESIGNINTENT(cls) -> IfcObjectiveEnum:
        ...
    
    @classmethod
    @property
    def HEALTHANDSAFETY(cls) -> IfcObjectiveEnum:
        ...
    
    @classmethod
    @property
    def REQUIREMENT(cls) -> IfcObjectiveEnum:
        ...
    
    @classmethod
    @property
    def SPECIFICATION(cls) -> IfcObjectiveEnum:
        ...
    
    @classmethod
    @property
    def TRIGGERCONDITION(cls) -> IfcObjectiveEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcObjectiveEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcObjectiveEnum:
        ...
    
    ...

class IfcOccupantTypeEnum:
    '''IfcOccupantTypeEnum'''
    
    @classmethod
    @property
    def ASSIGNEE(cls) -> IfcOccupantTypeEnum:
        ...
    
    @classmethod
    @property
    def ASSIGNOR(cls) -> IfcOccupantTypeEnum:
        ...
    
    @classmethod
    @property
    def LESSEE(cls) -> IfcOccupantTypeEnum:
        ...
    
    @classmethod
    @property
    def LESSOR(cls) -> IfcOccupantTypeEnum:
        ...
    
    @classmethod
    @property
    def LETTINGAGENT(cls) -> IfcOccupantTypeEnum:
        ...
    
    @classmethod
    @property
    def OWNER(cls) -> IfcOccupantTypeEnum:
        ...
    
    @classmethod
    @property
    def TENANT(cls) -> IfcOccupantTypeEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcOccupantTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcOccupantTypeEnum:
        ...
    
    ...

class IfcOutletTypeEnum:
    '''IfcOutletTypeEnum'''
    
    @classmethod
    @property
    def AUDIOVISUALOUTLET(cls) -> IfcOutletTypeEnum:
        ...
    
    @classmethod
    @property
    def COMMUNICATIONSOUTLET(cls) -> IfcOutletTypeEnum:
        ...
    
    @classmethod
    @property
    def POWEROUTLET(cls) -> IfcOutletTypeEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcOutletTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcOutletTypeEnum:
        ...
    
    ...

class IfcPermeableCoveringOperationEnum:
    '''IfcPermeableCoveringOperationEnum'''
    
    @classmethod
    @property
    def GRILL(cls) -> IfcPermeableCoveringOperationEnum:
        ...
    
    @classmethod
    @property
    def LOUVER(cls) -> IfcPermeableCoveringOperationEnum:
        ...
    
    @classmethod
    @property
    def SCREEN(cls) -> IfcPermeableCoveringOperationEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcPermeableCoveringOperationEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcPermeableCoveringOperationEnum:
        ...
    
    ...

class IfcPhysicalOrVirtualEnum:
    '''IfcPhysicalOrVirtualEnum'''
    
    @classmethod
    @property
    def PHYSICAL(cls) -> IfcPhysicalOrVirtualEnum:
        ...
    
    @classmethod
    @property
    def VIRTUAL(cls) -> IfcPhysicalOrVirtualEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcPhysicalOrVirtualEnum:
        ...
    
    ...

class IfcPileConstructionEnum:
    '''IfcPileConstructionEnum'''
    
    @classmethod
    @property
    def CAST_IN_PLACE(cls) -> IfcPileConstructionEnum:
        ...
    
    @classmethod
    @property
    def COMPOSITE(cls) -> IfcPileConstructionEnum:
        ...
    
    @classmethod
    @property
    def PRECAST_CONCRETE(cls) -> IfcPileConstructionEnum:
        ...
    
    @classmethod
    @property
    def PREFAB_STEEL(cls) -> IfcPileConstructionEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcPileConstructionEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcPileConstructionEnum:
        ...
    
    ...

class IfcPileTypeEnum:
    '''IfcPileTypeEnum'''
    
    @classmethod
    @property
    def COHESION(cls) -> IfcPileTypeEnum:
        ...
    
    @classmethod
    @property
    def FRICTION(cls) -> IfcPileTypeEnum:
        ...
    
    @classmethod
    @property
    def SUPPORT(cls) -> IfcPileTypeEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcPileTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcPileTypeEnum:
        ...
    
    ...

class IfcPipeFittingTypeEnum:
    '''IfcPipeFittingTypeEnum'''
    
    @classmethod
    @property
    def BEND(cls) -> IfcPipeFittingTypeEnum:
        ...
    
    @classmethod
    @property
    def CONNECTOR(cls) -> IfcPipeFittingTypeEnum:
        ...
    
    @classmethod
    @property
    def ENTRY(cls) -> IfcPipeFittingTypeEnum:
        ...
    
    @classmethod
    @property
    def EXIT(cls) -> IfcPipeFittingTypeEnum:
        ...
    
    @classmethod
    @property
    def JUNCTION(cls) -> IfcPipeFittingTypeEnum:
        ...
    
    @classmethod
    @property
    def OBSTRUCTION(cls) -> IfcPipeFittingTypeEnum:
        ...
    
    @classmethod
    @property
    def TRANSITION(cls) -> IfcPipeFittingTypeEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcPipeFittingTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcPipeFittingTypeEnum:
        ...
    
    ...

class IfcPipeSegmentTypeEnum:
    '''IfcPipeSegmentTypeEnum'''
    
    @classmethod
    @property
    def FLEXIBLESEGMENT(cls) -> IfcPipeSegmentTypeEnum:
        ...
    
    @classmethod
    @property
    def RIGIDSEGMENT(cls) -> IfcPipeSegmentTypeEnum:
        ...
    
    @classmethod
    @property
    def GUTTER(cls) -> IfcPipeSegmentTypeEnum:
        ...
    
    @classmethod
    @property
    def SPOOL(cls) -> IfcPipeSegmentTypeEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcPipeSegmentTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcPipeSegmentTypeEnum:
        ...
    
    ...

class IfcPlateTypeEnum:
    '''IfcPlateTypeEnum'''
    
    @classmethod
    @property
    def CURTAIN_PANEL(cls) -> IfcPlateTypeEnum:
        ...
    
    @classmethod
    @property
    def SHEET(cls) -> IfcPlateTypeEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcPlateTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcPlateTypeEnum:
        ...
    
    ...

class IfcProcedureTypeEnum:
    '''IfcProcedureTypeEnum'''
    
    @classmethod
    @property
    def ADVICE_CAUTION(cls) -> IfcProcedureTypeEnum:
        ...
    
    @classmethod
    @property
    def ADVICE_NOTE(cls) -> IfcProcedureTypeEnum:
        ...
    
    @classmethod
    @property
    def ADVICE_WARNING(cls) -> IfcProcedureTypeEnum:
        ...
    
    @classmethod
    @property
    def CALIBRATION(cls) -> IfcProcedureTypeEnum:
        ...
    
    @classmethod
    @property
    def DIAGNOSTIC(cls) -> IfcProcedureTypeEnum:
        ...
    
    @classmethod
    @property
    def SHUTDOWN(cls) -> IfcProcedureTypeEnum:
        ...
    
    @classmethod
    @property
    def STARTUP(cls) -> IfcProcedureTypeEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcProcedureTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcProcedureTypeEnum:
        ...
    
    ...

class IfcProfileTypeEnum:
    '''IfcProfileTypeEnum'''
    
    @classmethod
    @property
    def CURVE(cls) -> IfcProfileTypeEnum:
        ...
    
    @classmethod
    @property
    def AREA(cls) -> IfcProfileTypeEnum:
        ...
    
    ...

class IfcProjectOrderRecordTypeEnum:
    '''IfcProjectOrderRecordTypeEnum'''
    
    @classmethod
    @property
    def CHANGE(cls) -> IfcProjectOrderRecordTypeEnum:
        ...
    
    @classmethod
    @property
    def MAINTENANCE(cls) -> IfcProjectOrderRecordTypeEnum:
        ...
    
    @classmethod
    @property
    def MOVE(cls) -> IfcProjectOrderRecordTypeEnum:
        ...
    
    @classmethod
    @property
    def PURCHASE(cls) -> IfcProjectOrderRecordTypeEnum:
        ...
    
    @classmethod
    @property
    def WORK(cls) -> IfcProjectOrderRecordTypeEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcProjectOrderRecordTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcProjectOrderRecordTypeEnum:
        ...
    
    ...

class IfcProjectOrderTypeEnum:
    '''IfcProjectOrderTypeEnum'''
    
    @classmethod
    @property
    def CHANGEORDER(cls) -> IfcProjectOrderTypeEnum:
        ...
    
    @classmethod
    @property
    def MAINTENANCEWORKORDER(cls) -> IfcProjectOrderTypeEnum:
        ...
    
    @classmethod
    @property
    def MOVEORDER(cls) -> IfcProjectOrderTypeEnum:
        ...
    
    @classmethod
    @property
    def PURCHASEORDER(cls) -> IfcProjectOrderTypeEnum:
        ...
    
    @classmethod
    @property
    def WORKORDER(cls) -> IfcProjectOrderTypeEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcProjectOrderTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcProjectOrderTypeEnum:
        ...
    
    ...

class IfcProjectedOrTrueLengthEnum:
    '''IfcProjectedOrTrueLengthEnum'''
    
    @classmethod
    @property
    def PROJECTED_LENGTH(cls) -> IfcProjectedOrTrueLengthEnum:
        ...
    
    @classmethod
    @property
    def TRUE_LENGTH(cls) -> IfcProjectedOrTrueLengthEnum:
        ...
    
    ...

class IfcPropertySourceEnum:
    '''IfcPropertySourceEnum'''
    
    @classmethod
    @property
    def DESIGN(cls) -> IfcPropertySourceEnum:
        ...
    
    @classmethod
    @property
    def DESIGNMAXIMUM(cls) -> IfcPropertySourceEnum:
        ...
    
    @classmethod
    @property
    def DESIGNMINIMUM(cls) -> IfcPropertySourceEnum:
        ...
    
    @classmethod
    @property
    def SIMULATED(cls) -> IfcPropertySourceEnum:
        ...
    
    @classmethod
    @property
    def ASBUILT(cls) -> IfcPropertySourceEnum:
        ...
    
    @classmethod
    @property
    def COMMISSIONING(cls) -> IfcPropertySourceEnum:
        ...
    
    @classmethod
    @property
    def MEASURED(cls) -> IfcPropertySourceEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcPropertySourceEnum:
        ...
    
    @classmethod
    @property
    def NOTKNOWN(cls) -> IfcPropertySourceEnum:
        ...
    
    ...

class IfcProtectiveDeviceTypeEnum:
    '''IfcProtectiveDeviceTypeEnum'''
    
    @classmethod
    @property
    def FUSEDISCONNECTOR(cls) -> IfcProtectiveDeviceTypeEnum:
        ...
    
    @classmethod
    @property
    def CIRCUITBREAKER(cls) -> IfcProtectiveDeviceTypeEnum:
        ...
    
    @classmethod
    @property
    def EARTHFAILUREDEVICE(cls) -> IfcProtectiveDeviceTypeEnum:
        ...
    
    @classmethod
    @property
    def RESIDUALCURRENTCIRCUITBREAKER(cls) -> IfcProtectiveDeviceTypeEnum:
        ...
    
    @classmethod
    @property
    def RESIDUALCURRENTSWITCH(cls) -> IfcProtectiveDeviceTypeEnum:
        ...
    
    @classmethod
    @property
    def VARISTOR(cls) -> IfcProtectiveDeviceTypeEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcProtectiveDeviceTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcProtectiveDeviceTypeEnum:
        ...
    
    ...

class IfcPumpTypeEnum:
    '''IfcPumpTypeEnum'''
    
    @classmethod
    @property
    def CIRCULATOR(cls) -> IfcPumpTypeEnum:
        ...
    
    @classmethod
    @property
    def ENDSUCTION(cls) -> IfcPumpTypeEnum:
        ...
    
    @classmethod
    @property
    def SPLITCASE(cls) -> IfcPumpTypeEnum:
        ...
    
    @classmethod
    @property
    def VERTICALINLINE(cls) -> IfcPumpTypeEnum:
        ...
    
    @classmethod
    @property
    def VERTICALTURBINE(cls) -> IfcPumpTypeEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcPumpTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcPumpTypeEnum:
        ...
    
    ...

class IfcRailingTypeEnum:
    '''IfcRailingTypeEnum'''
    
    @classmethod
    @property
    def HANDRAIL(cls) -> IfcRailingTypeEnum:
        ...
    
    @classmethod
    @property
    def GUARDRAIL(cls) -> IfcRailingTypeEnum:
        ...
    
    @classmethod
    @property
    def BALUSTRADE(cls) -> IfcRailingTypeEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcRailingTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcRailingTypeEnum:
        ...
    
    ...

class IfcRampFlightTypeEnum:
    '''IfcRampFlightTypeEnum'''
    
    @classmethod
    @property
    def STRAIGHT(cls) -> IfcRampFlightTypeEnum:
        ...
    
    @classmethod
    @property
    def SPIRAL(cls) -> IfcRampFlightTypeEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcRampFlightTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcRampFlightTypeEnum:
        ...
    
    ...

class IfcRampTypeEnum:
    '''IfcRampTypeEnum'''
    
    @classmethod
    @property
    def STRAIGHT_RUN_RAMP(cls) -> IfcRampTypeEnum:
        ...
    
    @classmethod
    @property
    def TWO_STRAIGHT_RUN_RAMP(cls) -> IfcRampTypeEnum:
        ...
    
    @classmethod
    @property
    def QUARTER_TURN_RAMP(cls) -> IfcRampTypeEnum:
        ...
    
    @classmethod
    @property
    def TWO_QUARTER_TURN_RAMP(cls) -> IfcRampTypeEnum:
        ...
    
    @classmethod
    @property
    def HALF_TURN_RAMP(cls) -> IfcRampTypeEnum:
        ...
    
    @classmethod
    @property
    def SPIRAL_RAMP(cls) -> IfcRampTypeEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcRampTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcRampTypeEnum:
        ...
    
    ...

class IfcReflectanceMethodEnum:
    '''IfcReflectanceMethodEnum'''
    
    @classmethod
    @property
    def BLINN(cls) -> IfcReflectanceMethodEnum:
        ...
    
    @classmethod
    @property
    def FLAT(cls) -> IfcReflectanceMethodEnum:
        ...
    
    @classmethod
    @property
    def GLASS(cls) -> IfcReflectanceMethodEnum:
        ...
    
    @classmethod
    @property
    def MATT(cls) -> IfcReflectanceMethodEnum:
        ...
    
    @classmethod
    @property
    def METAL(cls) -> IfcReflectanceMethodEnum:
        ...
    
    @classmethod
    @property
    def MIRROR(cls) -> IfcReflectanceMethodEnum:
        ...
    
    @classmethod
    @property
    def PHONG(cls) -> IfcReflectanceMethodEnum:
        ...
    
    @classmethod
    @property
    def PLASTIC(cls) -> IfcReflectanceMethodEnum:
        ...
    
    @classmethod
    @property
    def STRAUSS(cls) -> IfcReflectanceMethodEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcReflectanceMethodEnum:
        ...
    
    ...

class IfcReinforcingBarRoleEnum:
    '''IfcReinforcingBarRoleEnum'''
    
    @classmethod
    @property
    def MAIN(cls) -> IfcReinforcingBarRoleEnum:
        ...
    
    @classmethod
    @property
    def SHEAR(cls) -> IfcReinforcingBarRoleEnum:
        ...
    
    @classmethod
    @property
    def LIGATURE(cls) -> IfcReinforcingBarRoleEnum:
        ...
    
    @classmethod
    @property
    def STUD(cls) -> IfcReinforcingBarRoleEnum:
        ...
    
    @classmethod
    @property
    def PUNCHING(cls) -> IfcReinforcingBarRoleEnum:
        ...
    
    @classmethod
    @property
    def EDGE(cls) -> IfcReinforcingBarRoleEnum:
        ...
    
    @classmethod
    @property
    def RING(cls) -> IfcReinforcingBarRoleEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcReinforcingBarRoleEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcReinforcingBarRoleEnum:
        ...
    
    ...

class IfcReinforcingBarSurfaceEnum:
    '''IfcReinforcingBarSurfaceEnum'''
    
    @classmethod
    @property
    def PLAIN(cls) -> IfcReinforcingBarSurfaceEnum:
        ...
    
    @classmethod
    @property
    def TEXTURED(cls) -> IfcReinforcingBarSurfaceEnum:
        ...
    
    ...

class IfcResourceConsumptionEnum:
    '''IfcResourceConsumptionEnum'''
    
    @classmethod
    @property
    def CONSUMED(cls) -> IfcResourceConsumptionEnum:
        ...
    
    @classmethod
    @property
    def PARTIALLYCONSUMED(cls) -> IfcResourceConsumptionEnum:
        ...
    
    @classmethod
    @property
    def NOTCONSUMED(cls) -> IfcResourceConsumptionEnum:
        ...
    
    @classmethod
    @property
    def OCCUPIED(cls) -> IfcResourceConsumptionEnum:
        ...
    
    @classmethod
    @property
    def PARTIALLYOCCUPIED(cls) -> IfcResourceConsumptionEnum:
        ...
    
    @classmethod
    @property
    def NOTOCCUPIED(cls) -> IfcResourceConsumptionEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcResourceConsumptionEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcResourceConsumptionEnum:
        ...
    
    ...

class IfcRibPlateDirectionEnum:
    '''IfcRibPlateDirectionEnum'''
    
    @classmethod
    @property
    def DIRECTION_X(cls) -> IfcRibPlateDirectionEnum:
        ...
    
    @classmethod
    @property
    def DIRECTION_Y(cls) -> IfcRibPlateDirectionEnum:
        ...
    
    ...

class IfcRoleEnum:
    '''IfcRoleEnum'''
    
    @classmethod
    @property
    def SUPPLIER(cls) -> IfcRoleEnum:
        ...
    
    @classmethod
    @property
    def MANUFACTURER(cls) -> IfcRoleEnum:
        ...
    
    @classmethod
    @property
    def CONTRACTOR(cls) -> IfcRoleEnum:
        ...
    
    @classmethod
    @property
    def SUBCONTRACTOR(cls) -> IfcRoleEnum:
        ...
    
    @classmethod
    @property
    def ARCHITECT(cls) -> IfcRoleEnum:
        ...
    
    @classmethod
    @property
    def STRUCTURALENGINEER(cls) -> IfcRoleEnum:
        ...
    
    @classmethod
    @property
    def COSTENGINEER(cls) -> IfcRoleEnum:
        ...
    
    @classmethod
    @property
    def CLIENT(cls) -> IfcRoleEnum:
        ...
    
    @classmethod
    @property
    def BUILDINGOWNER(cls) -> IfcRoleEnum:
        ...
    
    @classmethod
    @property
    def BUILDINGOPERATOR(cls) -> IfcRoleEnum:
        ...
    
    @classmethod
    @property
    def MECHANICALENGINEER(cls) -> IfcRoleEnum:
        ...
    
    @classmethod
    @property
    def ELECTRICALENGINEER(cls) -> IfcRoleEnum:
        ...
    
    @classmethod
    @property
    def PROJECTMANAGER(cls) -> IfcRoleEnum:
        ...
    
    @classmethod
    @property
    def FACILITIESMANAGER(cls) -> IfcRoleEnum:
        ...
    
    @classmethod
    @property
    def CIVILENGINEER(cls) -> IfcRoleEnum:
        ...
    
    @classmethod
    @property
    def COMISSIONINGENGINEER(cls) -> IfcRoleEnum:
        ...
    
    @classmethod
    @property
    def ENGINEER(cls) -> IfcRoleEnum:
        ...
    
    @classmethod
    @property
    def OWNER(cls) -> IfcRoleEnum:
        ...
    
    @classmethod
    @property
    def CONSULTANT(cls) -> IfcRoleEnum:
        ...
    
    @classmethod
    @property
    def CONSTRUCTIONMANAGER(cls) -> IfcRoleEnum:
        ...
    
    @classmethod
    @property
    def FIELDCONSTRUCTIONMANAGER(cls) -> IfcRoleEnum:
        ...
    
    @classmethod
    @property
    def RESELLER(cls) -> IfcRoleEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcRoleEnum:
        ...
    
    ...

class IfcRoofTypeEnum:
    '''IfcRoofTypeEnum'''
    
    @classmethod
    @property
    def FLAT_ROOF(cls) -> IfcRoofTypeEnum:
        ...
    
    @classmethod
    @property
    def SHED_ROOF(cls) -> IfcRoofTypeEnum:
        ...
    
    @classmethod
    @property
    def GABLE_ROOF(cls) -> IfcRoofTypeEnum:
        ...
    
    @classmethod
    @property
    def HIP_ROOF(cls) -> IfcRoofTypeEnum:
        ...
    
    @classmethod
    @property
    def HIPPED_GABLE_ROOF(cls) -> IfcRoofTypeEnum:
        ...
    
    @classmethod
    @property
    def GAMBREL_ROOF(cls) -> IfcRoofTypeEnum:
        ...
    
    @classmethod
    @property
    def MANSARD_ROOF(cls) -> IfcRoofTypeEnum:
        ...
    
    @classmethod
    @property
    def BARREL_ROOF(cls) -> IfcRoofTypeEnum:
        ...
    
    @classmethod
    @property
    def RAINBOW_ROOF(cls) -> IfcRoofTypeEnum:
        ...
    
    @classmethod
    @property
    def BUTTERFLY_ROOF(cls) -> IfcRoofTypeEnum:
        ...
    
    @classmethod
    @property
    def PAVILION_ROOF(cls) -> IfcRoofTypeEnum:
        ...
    
    @classmethod
    @property
    def DOME_ROOF(cls) -> IfcRoofTypeEnum:
        ...
    
    @classmethod
    @property
    def FREEFORM(cls) -> IfcRoofTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcRoofTypeEnum:
        ...
    
    ...

class IfcSIPrefix:
    '''IfcSIPrefix'''
    
    @classmethod
    @property
    def EXA(cls) -> IfcSIPrefix:
        ...
    
    @classmethod
    @property
    def PETA(cls) -> IfcSIPrefix:
        ...
    
    @classmethod
    @property
    def TERA(cls) -> IfcSIPrefix:
        ...
    
    @classmethod
    @property
    def GIGA(cls) -> IfcSIPrefix:
        ...
    
    @classmethod
    @property
    def MEGA(cls) -> IfcSIPrefix:
        ...
    
    @classmethod
    @property
    def KILO(cls) -> IfcSIPrefix:
        ...
    
    @classmethod
    @property
    def HECTO(cls) -> IfcSIPrefix:
        ...
    
    @classmethod
    @property
    def DECA(cls) -> IfcSIPrefix:
        ...
    
    @classmethod
    @property
    def DECI(cls) -> IfcSIPrefix:
        ...
    
    @classmethod
    @property
    def CENTI(cls) -> IfcSIPrefix:
        ...
    
    @classmethod
    @property
    def MILLI(cls) -> IfcSIPrefix:
        ...
    
    @classmethod
    @property
    def MICRO(cls) -> IfcSIPrefix:
        ...
    
    @classmethod
    @property
    def NANO(cls) -> IfcSIPrefix:
        ...
    
    @classmethod
    @property
    def PICO(cls) -> IfcSIPrefix:
        ...
    
    @classmethod
    @property
    def FEMTO(cls) -> IfcSIPrefix:
        ...
    
    @classmethod
    @property
    def ATTO(cls) -> IfcSIPrefix:
        ...
    
    ...

class IfcSIUnitName:
    '''IfcSIUnitName'''
    
    @classmethod
    @property
    def AMPERE(cls) -> IfcSIUnitName:
        ...
    
    @classmethod
    @property
    def BECQUEREL(cls) -> IfcSIUnitName:
        ...
    
    @classmethod
    @property
    def CANDELA(cls) -> IfcSIUnitName:
        ...
    
    @classmethod
    @property
    def COULOMB(cls) -> IfcSIUnitName:
        ...
    
    @classmethod
    @property
    def CUBIC_METRE(cls) -> IfcSIUnitName:
        ...
    
    @classmethod
    @property
    def DEGREE_CELSIUS(cls) -> IfcSIUnitName:
        ...
    
    @classmethod
    @property
    def FARAD(cls) -> IfcSIUnitName:
        ...
    
    @classmethod
    @property
    def GRAM(cls) -> IfcSIUnitName:
        ...
    
    @classmethod
    @property
    def GRAY(cls) -> IfcSIUnitName:
        ...
    
    @classmethod
    @property
    def HENRY(cls) -> IfcSIUnitName:
        ...
    
    @classmethod
    @property
    def HERTZ(cls) -> IfcSIUnitName:
        ...
    
    @classmethod
    @property
    def JOULE(cls) -> IfcSIUnitName:
        ...
    
    @classmethod
    @property
    def KELVIN(cls) -> IfcSIUnitName:
        ...
    
    @classmethod
    @property
    def LUMEN(cls) -> IfcSIUnitName:
        ...
    
    @classmethod
    @property
    def LUX(cls) -> IfcSIUnitName:
        ...
    
    @classmethod
    @property
    def METRE(cls) -> IfcSIUnitName:
        ...
    
    @classmethod
    @property
    def MOLE(cls) -> IfcSIUnitName:
        ...
    
    @classmethod
    @property
    def NEWTON(cls) -> IfcSIUnitName:
        ...
    
    @classmethod
    @property
    def OHM(cls) -> IfcSIUnitName:
        ...
    
    @classmethod
    @property
    def PASCAL(cls) -> IfcSIUnitName:
        ...
    
    @classmethod
    @property
    def RADIAN(cls) -> IfcSIUnitName:
        ...
    
    @classmethod
    @property
    def SECOND(cls) -> IfcSIUnitName:
        ...
    
    @classmethod
    @property
    def SIEMENS(cls) -> IfcSIUnitName:
        ...
    
    @classmethod
    @property
    def SIEVERT(cls) -> IfcSIUnitName:
        ...
    
    @classmethod
    @property
    def SQUARE_METRE(cls) -> IfcSIUnitName:
        ...
    
    @classmethod
    @property
    def STERADIAN(cls) -> IfcSIUnitName:
        ...
    
    @classmethod
    @property
    def TESLA(cls) -> IfcSIUnitName:
        ...
    
    @classmethod
    @property
    def VOLT(cls) -> IfcSIUnitName:
        ...
    
    @classmethod
    @property
    def WATT(cls) -> IfcSIUnitName:
        ...
    
    @classmethod
    @property
    def WEBER(cls) -> IfcSIUnitName:
        ...
    
    ...

class IfcSanitaryTerminalTypeEnum:
    '''IfcSanitaryTerminalTypeEnum'''
    
    @classmethod
    @property
    def BATH(cls) -> IfcSanitaryTerminalTypeEnum:
        ...
    
    @classmethod
    @property
    def BIDET(cls) -> IfcSanitaryTerminalTypeEnum:
        ...
    
    @classmethod
    @property
    def CISTERN(cls) -> IfcSanitaryTerminalTypeEnum:
        ...
    
    @classmethod
    @property
    def SHOWER(cls) -> IfcSanitaryTerminalTypeEnum:
        ...
    
    @classmethod
    @property
    def SINK(cls) -> IfcSanitaryTerminalTypeEnum:
        ...
    
    @classmethod
    @property
    def SANITARYFOUNTAIN(cls) -> IfcSanitaryTerminalTypeEnum:
        ...
    
    @classmethod
    @property
    def TOILETPAN(cls) -> IfcSanitaryTerminalTypeEnum:
        ...
    
    @classmethod
    @property
    def URINAL(cls) -> IfcSanitaryTerminalTypeEnum:
        ...
    
    @classmethod
    @property
    def WASHHANDBASIN(cls) -> IfcSanitaryTerminalTypeEnum:
        ...
    
    @classmethod
    @property
    def WCSEAT(cls) -> IfcSanitaryTerminalTypeEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcSanitaryTerminalTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcSanitaryTerminalTypeEnum:
        ...
    
    ...

class IfcSectionTypeEnum:
    '''IfcSectionTypeEnum'''
    
    @classmethod
    @property
    def UNIFORM(cls) -> IfcSectionTypeEnum:
        ...
    
    @classmethod
    @property
    def TAPERED(cls) -> IfcSectionTypeEnum:
        ...
    
    ...

class IfcSensorTypeEnum:
    '''IfcSensorTypeEnum'''
    
    @classmethod
    @property
    def CO2SENSOR(cls) -> IfcSensorTypeEnum:
        ...
    
    @classmethod
    @property
    def FIRESENSOR(cls) -> IfcSensorTypeEnum:
        ...
    
    @classmethod
    @property
    def FLOWSENSOR(cls) -> IfcSensorTypeEnum:
        ...
    
    @classmethod
    @property
    def GASSENSOR(cls) -> IfcSensorTypeEnum:
        ...
    
    @classmethod
    @property
    def HEATSENSOR(cls) -> IfcSensorTypeEnum:
        ...
    
    @classmethod
    @property
    def HUMIDITYSENSOR(cls) -> IfcSensorTypeEnum:
        ...
    
    @classmethod
    @property
    def LIGHTSENSOR(cls) -> IfcSensorTypeEnum:
        ...
    
    @classmethod
    @property
    def MOISTURESENSOR(cls) -> IfcSensorTypeEnum:
        ...
    
    @classmethod
    @property
    def MOVEMENTSENSOR(cls) -> IfcSensorTypeEnum:
        ...
    
    @classmethod
    @property
    def PRESSURESENSOR(cls) -> IfcSensorTypeEnum:
        ...
    
    @classmethod
    @property
    def SMOKESENSOR(cls) -> IfcSensorTypeEnum:
        ...
    
    @classmethod
    @property
    def SOUNDSENSOR(cls) -> IfcSensorTypeEnum:
        ...
    
    @classmethod
    @property
    def TEMPERATURESENSOR(cls) -> IfcSensorTypeEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcSensorTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcSensorTypeEnum:
        ...
    
    ...

class IfcSequenceEnum:
    '''IfcSequenceEnum'''
    
    @classmethod
    @property
    def START_START(cls) -> IfcSequenceEnum:
        ...
    
    @classmethod
    @property
    def START_FINISH(cls) -> IfcSequenceEnum:
        ...
    
    @classmethod
    @property
    def FINISH_START(cls) -> IfcSequenceEnum:
        ...
    
    @classmethod
    @property
    def FINISH_FINISH(cls) -> IfcSequenceEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcSequenceEnum:
        ...
    
    ...

class IfcServiceLifeFactorTypeEnum:
    '''IfcServiceLifeFactorTypeEnum'''
    
    @classmethod
    @property
    def A_QUALITYOFCOMPONENTS(cls) -> IfcServiceLifeFactorTypeEnum:
        ...
    
    @classmethod
    @property
    def B_DESIGNLEVEL(cls) -> IfcServiceLifeFactorTypeEnum:
        ...
    
    @classmethod
    @property
    def C_WORKEXECUTIONLEVEL(cls) -> IfcServiceLifeFactorTypeEnum:
        ...
    
    @classmethod
    @property
    def D_INDOORENVIRONMENT(cls) -> IfcServiceLifeFactorTypeEnum:
        ...
    
    @classmethod
    @property
    def E_OUTDOORENVIRONMENT(cls) -> IfcServiceLifeFactorTypeEnum:
        ...
    
    @classmethod
    @property
    def F_INUSECONDITIONS(cls) -> IfcServiceLifeFactorTypeEnum:
        ...
    
    @classmethod
    @property
    def G_MAINTENANCELEVEL(cls) -> IfcServiceLifeFactorTypeEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcServiceLifeFactorTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcServiceLifeFactorTypeEnum:
        ...
    
    ...

class IfcServiceLifeTypeEnum:
    '''IfcServiceLifeTypeEnum'''
    
    @classmethod
    @property
    def ACTUALSERVICELIFE(cls) -> IfcServiceLifeTypeEnum:
        ...
    
    @classmethod
    @property
    def EXPECTEDSERVICELIFE(cls) -> IfcServiceLifeTypeEnum:
        ...
    
    @classmethod
    @property
    def OPTIMISTICREFERENCESERVICELIFE(cls) -> IfcServiceLifeTypeEnum:
        ...
    
    @classmethod
    @property
    def PESSIMISTICREFERENCESERVICELIFE(cls) -> IfcServiceLifeTypeEnum:
        ...
    
    @classmethod
    @property
    def REFERENCESERVICELIFE(cls) -> IfcServiceLifeTypeEnum:
        ...
    
    ...

class IfcSlabTypeEnum:
    '''IfcSlabTypeEnum'''
    
    @classmethod
    @property
    def FLOOR(cls) -> IfcSlabTypeEnum:
        ...
    
    @classmethod
    @property
    def ROOF(cls) -> IfcSlabTypeEnum:
        ...
    
    @classmethod
    @property
    def LANDING(cls) -> IfcSlabTypeEnum:
        ...
    
    @classmethod
    @property
    def BASESLAB(cls) -> IfcSlabTypeEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcSlabTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcSlabTypeEnum:
        ...
    
    ...

class IfcSoundScaleEnum:
    '''IfcSoundScaleEnum'''
    
    @classmethod
    @property
    def DBA(cls) -> IfcSoundScaleEnum:
        ...
    
    @classmethod
    @property
    def DBB(cls) -> IfcSoundScaleEnum:
        ...
    
    @classmethod
    @property
    def DBC(cls) -> IfcSoundScaleEnum:
        ...
    
    @classmethod
    @property
    def NC(cls) -> IfcSoundScaleEnum:
        ...
    
    @classmethod
    @property
    def NR(cls) -> IfcSoundScaleEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcSoundScaleEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcSoundScaleEnum:
        ...
    
    ...

class IfcSpaceHeaterTypeEnum:
    '''IfcSpaceHeaterTypeEnum'''
    
    @classmethod
    @property
    def SECTIONALRADIATOR(cls) -> IfcSpaceHeaterTypeEnum:
        ...
    
    @classmethod
    @property
    def PANELRADIATOR(cls) -> IfcSpaceHeaterTypeEnum:
        ...
    
    @classmethod
    @property
    def TUBULARRADIATOR(cls) -> IfcSpaceHeaterTypeEnum:
        ...
    
    @classmethod
    @property
    def CONVECTOR(cls) -> IfcSpaceHeaterTypeEnum:
        ...
    
    @classmethod
    @property
    def BASEBOARDHEATER(cls) -> IfcSpaceHeaterTypeEnum:
        ...
    
    @classmethod
    @property
    def FINNEDTUBEUNIT(cls) -> IfcSpaceHeaterTypeEnum:
        ...
    
    @classmethod
    @property
    def UNITHEATER(cls) -> IfcSpaceHeaterTypeEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcSpaceHeaterTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcSpaceHeaterTypeEnum:
        ...
    
    ...

class IfcSpaceTypeEnum:
    '''IfcSpaceTypeEnum'''
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcSpaceTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcSpaceTypeEnum:
        ...
    
    ...

class IfcStackTerminalTypeEnum:
    '''IfcStackTerminalTypeEnum'''
    
    @classmethod
    @property
    def BIRDCAGE(cls) -> IfcStackTerminalTypeEnum:
        ...
    
    @classmethod
    @property
    def COWL(cls) -> IfcStackTerminalTypeEnum:
        ...
    
    @classmethod
    @property
    def RAINWATERHOPPER(cls) -> IfcStackTerminalTypeEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcStackTerminalTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcStackTerminalTypeEnum:
        ...
    
    ...

class IfcStairFlightTypeEnum:
    '''IfcStairFlightTypeEnum'''
    
    @classmethod
    @property
    def STRAIGHT(cls) -> IfcStairFlightTypeEnum:
        ...
    
    @classmethod
    @property
    def WINDER(cls) -> IfcStairFlightTypeEnum:
        ...
    
    @classmethod
    @property
    def SPIRAL(cls) -> IfcStairFlightTypeEnum:
        ...
    
    @classmethod
    @property
    def CURVED(cls) -> IfcStairFlightTypeEnum:
        ...
    
    @classmethod
    @property
    def FREEFORM(cls) -> IfcStairFlightTypeEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcStairFlightTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcStairFlightTypeEnum:
        ...
    
    ...

class IfcStairTypeEnum:
    '''IfcStairTypeEnum'''
    
    @classmethod
    @property
    def STRAIGHT_RUN_STAIR(cls) -> IfcStairTypeEnum:
        ...
    
    @classmethod
    @property
    def TWO_STRAIGHT_RUN_STAIR(cls) -> IfcStairTypeEnum:
        ...
    
    @classmethod
    @property
    def QUARTER_WINDING_STAIR(cls) -> IfcStairTypeEnum:
        ...
    
    @classmethod
    @property
    def QUARTER_TURN_STAIR(cls) -> IfcStairTypeEnum:
        ...
    
    @classmethod
    @property
    def HALF_WINDING_STAIR(cls) -> IfcStairTypeEnum:
        ...
    
    @classmethod
    @property
    def HALF_TURN_STAIR(cls) -> IfcStairTypeEnum:
        ...
    
    @classmethod
    @property
    def TWO_QUARTER_WINDING_STAIR(cls) -> IfcStairTypeEnum:
        ...
    
    @classmethod
    @property
    def TWO_QUARTER_TURN_STAIR(cls) -> IfcStairTypeEnum:
        ...
    
    @classmethod
    @property
    def THREE_QUARTER_WINDING_STAIR(cls) -> IfcStairTypeEnum:
        ...
    
    @classmethod
    @property
    def THREE_QUARTER_TURN_STAIR(cls) -> IfcStairTypeEnum:
        ...
    
    @classmethod
    @property
    def SPIRAL_STAIR(cls) -> IfcStairTypeEnum:
        ...
    
    @classmethod
    @property
    def DOUBLE_RETURN_STAIR(cls) -> IfcStairTypeEnum:
        ...
    
    @classmethod
    @property
    def CURVED_RUN_STAIR(cls) -> IfcStairTypeEnum:
        ...
    
    @classmethod
    @property
    def TWO_CURVED_RUN_STAIR(cls) -> IfcStairTypeEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcStairTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcStairTypeEnum:
        ...
    
    ...

class IfcStateEnum:
    '''IfcStateEnum'''
    
    @classmethod
    @property
    def READWRITE(cls) -> IfcStateEnum:
        ...
    
    @classmethod
    @property
    def READONLY(cls) -> IfcStateEnum:
        ...
    
    @classmethod
    @property
    def LOCKED(cls) -> IfcStateEnum:
        ...
    
    @classmethod
    @property
    def READWRITELOCKED(cls) -> IfcStateEnum:
        ...
    
    @classmethod
    @property
    def READONLYLOCKED(cls) -> IfcStateEnum:
        ...
    
    ...

class IfcStructuralCurveTypeEnum:
    '''IfcStructuralCurveTypeEnum'''
    
    @classmethod
    @property
    def RIGID_JOINED_MEMBER(cls) -> IfcStructuralCurveTypeEnum:
        ...
    
    @classmethod
    @property
    def PIN_JOINED_MEMBER(cls) -> IfcStructuralCurveTypeEnum:
        ...
    
    @classmethod
    @property
    def CABLE(cls) -> IfcStructuralCurveTypeEnum:
        ...
    
    @classmethod
    @property
    def TENSION_MEMBER(cls) -> IfcStructuralCurveTypeEnum:
        ...
    
    @classmethod
    @property
    def COMPRESSION_MEMBER(cls) -> IfcStructuralCurveTypeEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcStructuralCurveTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcStructuralCurveTypeEnum:
        ...
    
    ...

class IfcStructuralSurfaceTypeEnum:
    '''IfcStructuralSurfaceTypeEnum'''
    
    @classmethod
    @property
    def BENDING_ELEMENT(cls) -> IfcStructuralSurfaceTypeEnum:
        ...
    
    @classmethod
    @property
    def MEMBRANE_ELEMENT(cls) -> IfcStructuralSurfaceTypeEnum:
        ...
    
    @classmethod
    @property
    def SHELL(cls) -> IfcStructuralSurfaceTypeEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcStructuralSurfaceTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcStructuralSurfaceTypeEnum:
        ...
    
    ...

class IfcSurfaceSide:
    '''IfcSurfaceSide'''
    
    @classmethod
    @property
    def POSITIVE(cls) -> IfcSurfaceSide:
        ...
    
    @classmethod
    @property
    def NEGATIVE(cls) -> IfcSurfaceSide:
        ...
    
    @classmethod
    @property
    def BOTH(cls) -> IfcSurfaceSide:
        ...
    
    ...

class IfcSurfaceTextureEnum:
    '''IfcSurfaceTextureEnum'''
    
    @classmethod
    @property
    def BUMP(cls) -> IfcSurfaceTextureEnum:
        ...
    
    @classmethod
    @property
    def OPACITY(cls) -> IfcSurfaceTextureEnum:
        ...
    
    @classmethod
    @property
    def REFLECTION(cls) -> IfcSurfaceTextureEnum:
        ...
    
    @classmethod
    @property
    def SELFILLUMINATION(cls) -> IfcSurfaceTextureEnum:
        ...
    
    @classmethod
    @property
    def SHININESS(cls) -> IfcSurfaceTextureEnum:
        ...
    
    @classmethod
    @property
    def SPECULAR(cls) -> IfcSurfaceTextureEnum:
        ...
    
    @classmethod
    @property
    def TEXTURE(cls) -> IfcSurfaceTextureEnum:
        ...
    
    @classmethod
    @property
    def TRANSPARENCYMAP(cls) -> IfcSurfaceTextureEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcSurfaceTextureEnum:
        ...
    
    ...

class IfcSwitchingDeviceTypeEnum:
    '''IfcSwitchingDeviceTypeEnum'''
    
    @classmethod
    @property
    def CONTACTOR(cls) -> IfcSwitchingDeviceTypeEnum:
        ...
    
    @classmethod
    @property
    def EMERGENCYSTOP(cls) -> IfcSwitchingDeviceTypeEnum:
        ...
    
    @classmethod
    @property
    def STARTER(cls) -> IfcSwitchingDeviceTypeEnum:
        ...
    
    @classmethod
    @property
    def SWITCHDISCONNECTOR(cls) -> IfcSwitchingDeviceTypeEnum:
        ...
    
    @classmethod
    @property
    def TOGGLESWITCH(cls) -> IfcSwitchingDeviceTypeEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcSwitchingDeviceTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcSwitchingDeviceTypeEnum:
        ...
    
    ...

class IfcTankTypeEnum:
    '''IfcTankTypeEnum'''
    
    @classmethod
    @property
    def PREFORMED(cls) -> IfcTankTypeEnum:
        ...
    
    @classmethod
    @property
    def SECTIONAL(cls) -> IfcTankTypeEnum:
        ...
    
    @classmethod
    @property
    def EXPANSION(cls) -> IfcTankTypeEnum:
        ...
    
    @classmethod
    @property
    def PRESSUREVESSEL(cls) -> IfcTankTypeEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcTankTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcTankTypeEnum:
        ...
    
    ...

class IfcTendonTypeEnum:
    '''IfcTendonTypeEnum'''
    
    @classmethod
    @property
    def STRAND(cls) -> IfcTendonTypeEnum:
        ...
    
    @classmethod
    @property
    def WIRE(cls) -> IfcTendonTypeEnum:
        ...
    
    @classmethod
    @property
    def BAR(cls) -> IfcTendonTypeEnum:
        ...
    
    @classmethod
    @property
    def COATED(cls) -> IfcTendonTypeEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcTendonTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcTendonTypeEnum:
        ...
    
    ...

class IfcTextPath:
    '''IfcTextPath'''
    
    @classmethod
    @property
    def LEFT(cls) -> IfcTextPath:
        ...
    
    @classmethod
    @property
    def RIGHT(cls) -> IfcTextPath:
        ...
    
    @classmethod
    @property
    def UP(cls) -> IfcTextPath:
        ...
    
    @classmethod
    @property
    def DOWN(cls) -> IfcTextPath:
        ...
    
    ...

class IfcThermalLoadSourceEnum:
    '''IfcThermalLoadSourceEnum'''
    
    @classmethod
    @property
    def PEOPLE(cls) -> IfcThermalLoadSourceEnum:
        ...
    
    @classmethod
    @property
    def LIGHTING(cls) -> IfcThermalLoadSourceEnum:
        ...
    
    @classmethod
    @property
    def EQUIPMENT(cls) -> IfcThermalLoadSourceEnum:
        ...
    
    @classmethod
    @property
    def VENTILATIONINDOORAIR(cls) -> IfcThermalLoadSourceEnum:
        ...
    
    @classmethod
    @property
    def VENTILATIONOUTSIDEAIR(cls) -> IfcThermalLoadSourceEnum:
        ...
    
    @classmethod
    @property
    def RECIRCULATEDAIR(cls) -> IfcThermalLoadSourceEnum:
        ...
    
    @classmethod
    @property
    def EXHAUSTAIR(cls) -> IfcThermalLoadSourceEnum:
        ...
    
    @classmethod
    @property
    def AIREXCHANGERATE(cls) -> IfcThermalLoadSourceEnum:
        ...
    
    @classmethod
    @property
    def DRYBULBTEMPERATURE(cls) -> IfcThermalLoadSourceEnum:
        ...
    
    @classmethod
    @property
    def RELATIVEHUMIDITY(cls) -> IfcThermalLoadSourceEnum:
        ...
    
    @classmethod
    @property
    def INFILTRATION(cls) -> IfcThermalLoadSourceEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcThermalLoadSourceEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcThermalLoadSourceEnum:
        ...
    
    ...

class IfcThermalLoadTypeEnum:
    '''IfcThermalLoadTypeEnum'''
    
    @classmethod
    @property
    def SENSIBLE(cls) -> IfcThermalLoadTypeEnum:
        ...
    
    @classmethod
    @property
    def LATENT(cls) -> IfcThermalLoadTypeEnum:
        ...
    
    @classmethod
    @property
    def RADIANT(cls) -> IfcThermalLoadTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcThermalLoadTypeEnum:
        ...
    
    ...

class IfcTimeSeriesDataTypeEnum:
    '''IfcTimeSeriesDataTypeEnum'''
    
    @classmethod
    @property
    def CONTINUOUS(cls) -> IfcTimeSeriesDataTypeEnum:
        ...
    
    @classmethod
    @property
    def DISCRETE(cls) -> IfcTimeSeriesDataTypeEnum:
        ...
    
    @classmethod
    @property
    def DISCRETEBINARY(cls) -> IfcTimeSeriesDataTypeEnum:
        ...
    
    @classmethod
    @property
    def PIECEWISEBINARY(cls) -> IfcTimeSeriesDataTypeEnum:
        ...
    
    @classmethod
    @property
    def PIECEWISECONSTANT(cls) -> IfcTimeSeriesDataTypeEnum:
        ...
    
    @classmethod
    @property
    def PIECEWISECONTINUOUS(cls) -> IfcTimeSeriesDataTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcTimeSeriesDataTypeEnum:
        ...
    
    ...

class IfcTimeSeriesScheduleTypeEnum:
    '''IfcTimeSeriesScheduleTypeEnum'''
    
    @classmethod
    @property
    def ANNUAL(cls) -> IfcTimeSeriesScheduleTypeEnum:
        ...
    
    @classmethod
    @property
    def MONTHLY(cls) -> IfcTimeSeriesScheduleTypeEnum:
        ...
    
    @classmethod
    @property
    def WEEKLY(cls) -> IfcTimeSeriesScheduleTypeEnum:
        ...
    
    @classmethod
    @property
    def DAILY(cls) -> IfcTimeSeriesScheduleTypeEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcTimeSeriesScheduleTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcTimeSeriesScheduleTypeEnum:
        ...
    
    ...

class IfcTransformerTypeEnum:
    '''IfcTransformerTypeEnum'''
    
    @classmethod
    @property
    def CURRENT(cls) -> IfcTransformerTypeEnum:
        ...
    
    @classmethod
    @property
    def FREQUENCY(cls) -> IfcTransformerTypeEnum:
        ...
    
    @classmethod
    @property
    def VOLTAGE(cls) -> IfcTransformerTypeEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcTransformerTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcTransformerTypeEnum:
        ...
    
    ...

class IfcTransitionCode:
    '''IfcTransitionCode'''
    
    @classmethod
    @property
    def DISCONTINUOUS(cls) -> IfcTransitionCode:
        ...
    
    @classmethod
    @property
    def CONTINUOUS(cls) -> IfcTransitionCode:
        ...
    
    @classmethod
    @property
    def CONTSAMEGRADIENT(cls) -> IfcTransitionCode:
        ...
    
    @classmethod
    @property
    def CONTSAMEGRADIENTSAMECURVATURE(cls) -> IfcTransitionCode:
        ...
    
    ...

class IfcTransportElementTypeEnum:
    '''IfcTransportElementTypeEnum'''
    
    @classmethod
    @property
    def ELEVATOR(cls) -> IfcTransportElementTypeEnum:
        ...
    
    @classmethod
    @property
    def ESCALATOR(cls) -> IfcTransportElementTypeEnum:
        ...
    
    @classmethod
    @property
    def MOVINGWALKWAY(cls) -> IfcTransportElementTypeEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcTransportElementTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcTransportElementTypeEnum:
        ...
    
    ...

class IfcTrimmingPreference:
    '''IfcTrimmingPreference'''
    
    @classmethod
    @property
    def CARTESIAN(cls) -> IfcTrimmingPreference:
        ...
    
    @classmethod
    @property
    def PARAMETER(cls) -> IfcTrimmingPreference:
        ...
    
    @classmethod
    @property
    def UNSPECIFIED(cls) -> IfcTrimmingPreference:
        ...
    
    ...

class IfcTubeBundleTypeEnum:
    '''IfcTubeBundleTypeEnum'''
    
    @classmethod
    @property
    def FINNED(cls) -> IfcTubeBundleTypeEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcTubeBundleTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcTubeBundleTypeEnum:
        ...
    
    ...

class IfcUnitEnum:
    '''IfcUnitEnum'''
    
    @classmethod
    @property
    def ABSORBEDDOSEUNIT(cls) -> IfcUnitEnum:
        ...
    
    @classmethod
    @property
    def AMOUNTOFSUBSTANCEUNIT(cls) -> IfcUnitEnum:
        ...
    
    @classmethod
    @property
    def AREAUNIT(cls) -> IfcUnitEnum:
        ...
    
    @classmethod
    @property
    def DOSEEQUIVALENTUNIT(cls) -> IfcUnitEnum:
        ...
    
    @classmethod
    @property
    def ELECTRICCAPACITANCEUNIT(cls) -> IfcUnitEnum:
        ...
    
    @classmethod
    @property
    def ELECTRICCHARGEUNIT(cls) -> IfcUnitEnum:
        ...
    
    @classmethod
    @property
    def ELECTRICCONDUCTANCEUNIT(cls) -> IfcUnitEnum:
        ...
    
    @classmethod
    @property
    def ELECTRICCURRENTUNIT(cls) -> IfcUnitEnum:
        ...
    
    @classmethod
    @property
    def ELECTRICRESISTANCEUNIT(cls) -> IfcUnitEnum:
        ...
    
    @classmethod
    @property
    def ELECTRICVOLTAGEUNIT(cls) -> IfcUnitEnum:
        ...
    
    @classmethod
    @property
    def ENERGYUNIT(cls) -> IfcUnitEnum:
        ...
    
    @classmethod
    @property
    def FORCEUNIT(cls) -> IfcUnitEnum:
        ...
    
    @classmethod
    @property
    def FREQUENCYUNIT(cls) -> IfcUnitEnum:
        ...
    
    @classmethod
    @property
    def ILLUMINANCEUNIT(cls) -> IfcUnitEnum:
        ...
    
    @classmethod
    @property
    def INDUCTANCEUNIT(cls) -> IfcUnitEnum:
        ...
    
    @classmethod
    @property
    def LENGTHUNIT(cls) -> IfcUnitEnum:
        ...
    
    @classmethod
    @property
    def LUMINOUSFLUXUNIT(cls) -> IfcUnitEnum:
        ...
    
    @classmethod
    @property
    def LUMINOUSINTENSITYUNIT(cls) -> IfcUnitEnum:
        ...
    
    @classmethod
    @property
    def MAGNETICFLUXDENSITYUNIT(cls) -> IfcUnitEnum:
        ...
    
    @classmethod
    @property
    def MAGNETICFLUXUNIT(cls) -> IfcUnitEnum:
        ...
    
    @classmethod
    @property
    def MASSUNIT(cls) -> IfcUnitEnum:
        ...
    
    @classmethod
    @property
    def PLANEANGLEUNIT(cls) -> IfcUnitEnum:
        ...
    
    @classmethod
    @property
    def POWERUNIT(cls) -> IfcUnitEnum:
        ...
    
    @classmethod
    @property
    def PRESSUREUNIT(cls) -> IfcUnitEnum:
        ...
    
    @classmethod
    @property
    def RADIOACTIVITYUNIT(cls) -> IfcUnitEnum:
        ...
    
    @classmethod
    @property
    def SOLIDANGLEUNIT(cls) -> IfcUnitEnum:
        ...
    
    @classmethod
    @property
    def THERMODYNAMICTEMPERATUREUNIT(cls) -> IfcUnitEnum:
        ...
    
    @classmethod
    @property
    def TIMEUNIT(cls) -> IfcUnitEnum:
        ...
    
    @classmethod
    @property
    def VOLUMEUNIT(cls) -> IfcUnitEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcUnitEnum:
        ...
    
    ...

class IfcUnitaryEquipmentTypeEnum:
    '''IfcUnitaryEquipmentTypeEnum'''
    
    @classmethod
    @property
    def AIRHANDLER(cls) -> IfcUnitaryEquipmentTypeEnum:
        ...
    
    @classmethod
    @property
    def AIRCONDITIONINGUNIT(cls) -> IfcUnitaryEquipmentTypeEnum:
        ...
    
    @classmethod
    @property
    def SPLITSYSTEM(cls) -> IfcUnitaryEquipmentTypeEnum:
        ...
    
    @classmethod
    @property
    def ROOFTOPUNIT(cls) -> IfcUnitaryEquipmentTypeEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcUnitaryEquipmentTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcUnitaryEquipmentTypeEnum:
        ...
    
    ...

class IfcValveTypeEnum:
    '''IfcValveTypeEnum'''
    
    @classmethod
    @property
    def AIRRELEASE(cls) -> IfcValveTypeEnum:
        ...
    
    @classmethod
    @property
    def ANTIVACUUM(cls) -> IfcValveTypeEnum:
        ...
    
    @classmethod
    @property
    def CHANGEOVER(cls) -> IfcValveTypeEnum:
        ...
    
    @classmethod
    @property
    def CHECK(cls) -> IfcValveTypeEnum:
        ...
    
    @classmethod
    @property
    def COMMISSIONING(cls) -> IfcValveTypeEnum:
        ...
    
    @classmethod
    @property
    def DIVERTING(cls) -> IfcValveTypeEnum:
        ...
    
    @classmethod
    @property
    def DRAWOFFCOCK(cls) -> IfcValveTypeEnum:
        ...
    
    @classmethod
    @property
    def DOUBLECHECK(cls) -> IfcValveTypeEnum:
        ...
    
    @classmethod
    @property
    def DOUBLEREGULATING(cls) -> IfcValveTypeEnum:
        ...
    
    @classmethod
    @property
    def FAUCET(cls) -> IfcValveTypeEnum:
        ...
    
    @classmethod
    @property
    def FLUSHING(cls) -> IfcValveTypeEnum:
        ...
    
    @classmethod
    @property
    def GASCOCK(cls) -> IfcValveTypeEnum:
        ...
    
    @classmethod
    @property
    def GASTAP(cls) -> IfcValveTypeEnum:
        ...
    
    @classmethod
    @property
    def ISOLATING(cls) -> IfcValveTypeEnum:
        ...
    
    @classmethod
    @property
    def MIXING(cls) -> IfcValveTypeEnum:
        ...
    
    @classmethod
    @property
    def PRESSUREREDUCING(cls) -> IfcValveTypeEnum:
        ...
    
    @classmethod
    @property
    def PRESSURERELIEF(cls) -> IfcValveTypeEnum:
        ...
    
    @classmethod
    @property
    def REGULATING(cls) -> IfcValveTypeEnum:
        ...
    
    @classmethod
    @property
    def SAFETYCUTOFF(cls) -> IfcValveTypeEnum:
        ...
    
    @classmethod
    @property
    def STEAMTRAP(cls) -> IfcValveTypeEnum:
        ...
    
    @classmethod
    @property
    def STOPCOCK(cls) -> IfcValveTypeEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcValveTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcValveTypeEnum:
        ...
    
    ...

class IfcVibrationIsolatorTypeEnum:
    '''IfcVibrationIsolatorTypeEnum'''
    
    @classmethod
    @property
    def COMPRESSION(cls) -> IfcVibrationIsolatorTypeEnum:
        ...
    
    @classmethod
    @property
    def SPRING(cls) -> IfcVibrationIsolatorTypeEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcVibrationIsolatorTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcVibrationIsolatorTypeEnum:
        ...
    
    ...

class IfcWallTypeEnum:
    '''IfcWallTypeEnum'''
    
    @classmethod
    @property
    def STANDARD(cls) -> IfcWallTypeEnum:
        ...
    
    @classmethod
    @property
    def POLYGONAL(cls) -> IfcWallTypeEnum:
        ...
    
    @classmethod
    @property
    def SHEAR(cls) -> IfcWallTypeEnum:
        ...
    
    @classmethod
    @property
    def ELEMENTEDWALL(cls) -> IfcWallTypeEnum:
        ...
    
    @classmethod
    @property
    def PLUMBINGWALL(cls) -> IfcWallTypeEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcWallTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcWallTypeEnum:
        ...
    
    ...

class IfcWasteTerminalTypeEnum:
    '''IfcWasteTerminalTypeEnum'''
    
    @classmethod
    @property
    def FLOORTRAP(cls) -> IfcWasteTerminalTypeEnum:
        ...
    
    @classmethod
    @property
    def FLOORWASTE(cls) -> IfcWasteTerminalTypeEnum:
        ...
    
    @classmethod
    @property
    def GULLYSUMP(cls) -> IfcWasteTerminalTypeEnum:
        ...
    
    @classmethod
    @property
    def GULLYTRAP(cls) -> IfcWasteTerminalTypeEnum:
        ...
    
    @classmethod
    @property
    def GREASEINTERCEPTOR(cls) -> IfcWasteTerminalTypeEnum:
        ...
    
    @classmethod
    @property
    def OILINTERCEPTOR(cls) -> IfcWasteTerminalTypeEnum:
        ...
    
    @classmethod
    @property
    def PETROLINTERCEPTOR(cls) -> IfcWasteTerminalTypeEnum:
        ...
    
    @classmethod
    @property
    def ROOFDRAIN(cls) -> IfcWasteTerminalTypeEnum:
        ...
    
    @classmethod
    @property
    def WASTEDISPOSALUNIT(cls) -> IfcWasteTerminalTypeEnum:
        ...
    
    @classmethod
    @property
    def WASTETRAP(cls) -> IfcWasteTerminalTypeEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcWasteTerminalTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcWasteTerminalTypeEnum:
        ...
    
    ...

class IfcWindowPanelOperationEnum:
    '''IfcWindowPanelOperationEnum'''
    
    @classmethod
    @property
    def SIDEHUNGRIGHTHAND(cls) -> IfcWindowPanelOperationEnum:
        ...
    
    @classmethod
    @property
    def SIDEHUNGLEFTHAND(cls) -> IfcWindowPanelOperationEnum:
        ...
    
    @classmethod
    @property
    def TILTANDTURNRIGHTHAND(cls) -> IfcWindowPanelOperationEnum:
        ...
    
    @classmethod
    @property
    def TILTANDTURNLEFTHAND(cls) -> IfcWindowPanelOperationEnum:
        ...
    
    @classmethod
    @property
    def TOPHUNG(cls) -> IfcWindowPanelOperationEnum:
        ...
    
    @classmethod
    @property
    def BOTTOMHUNG(cls) -> IfcWindowPanelOperationEnum:
        ...
    
    @classmethod
    @property
    def PIVOTHORIZONTAL(cls) -> IfcWindowPanelOperationEnum:
        ...
    
    @classmethod
    @property
    def PIVOTVERTICAL(cls) -> IfcWindowPanelOperationEnum:
        ...
    
    @classmethod
    @property
    def SLIDINGHORIZONTAL(cls) -> IfcWindowPanelOperationEnum:
        ...
    
    @classmethod
    @property
    def SLIDINGVERTICAL(cls) -> IfcWindowPanelOperationEnum:
        ...
    
    @classmethod
    @property
    def REMOVABLECASEMENT(cls) -> IfcWindowPanelOperationEnum:
        ...
    
    @classmethod
    @property
    def FIXEDCASEMENT(cls) -> IfcWindowPanelOperationEnum:
        ...
    
    @classmethod
    @property
    def OTHEROPERATION(cls) -> IfcWindowPanelOperationEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcWindowPanelOperationEnum:
        ...
    
    ...

class IfcWindowPanelPositionEnum:
    '''IfcWindowPanelPositionEnum'''
    
    @classmethod
    @property
    def LEFT(cls) -> IfcWindowPanelPositionEnum:
        ...
    
    @classmethod
    @property
    def MIDDLE(cls) -> IfcWindowPanelPositionEnum:
        ...
    
    @classmethod
    @property
    def RIGHT(cls) -> IfcWindowPanelPositionEnum:
        ...
    
    @classmethod
    @property
    def BOTTOM(cls) -> IfcWindowPanelPositionEnum:
        ...
    
    @classmethod
    @property
    def TOP(cls) -> IfcWindowPanelPositionEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcWindowPanelPositionEnum:
        ...
    
    ...

class IfcWindowStyleConstructionEnum:
    '''IfcWindowStyleConstructionEnum'''
    
    @classmethod
    @property
    def ALUMINIUM(cls) -> IfcWindowStyleConstructionEnum:
        ...
    
    @classmethod
    @property
    def HIGH_GRADE_STEEL(cls) -> IfcWindowStyleConstructionEnum:
        ...
    
    @classmethod
    @property
    def STEEL(cls) -> IfcWindowStyleConstructionEnum:
        ...
    
    @classmethod
    @property
    def WOOD(cls) -> IfcWindowStyleConstructionEnum:
        ...
    
    @classmethod
    @property
    def ALUMINIUM_WOOD(cls) -> IfcWindowStyleConstructionEnum:
        ...
    
    @classmethod
    @property
    def PLASTIC(cls) -> IfcWindowStyleConstructionEnum:
        ...
    
    @classmethod
    @property
    def OTHER_CONSTRUCTION(cls) -> IfcWindowStyleConstructionEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcWindowStyleConstructionEnum:
        ...
    
    ...

class IfcWindowStyleOperationEnum:
    '''IfcWindowStyleOperationEnum'''
    
    @classmethod
    @property
    def SINGLE_PANEL(cls) -> IfcWindowStyleOperationEnum:
        ...
    
    @classmethod
    @property
    def DOUBLE_PANEL_VERTICAL(cls) -> IfcWindowStyleOperationEnum:
        ...
    
    @classmethod
    @property
    def DOUBLE_PANEL_HORIZONTAL(cls) -> IfcWindowStyleOperationEnum:
        ...
    
    @classmethod
    @property
    def TRIPLE_PANEL_VERTICAL(cls) -> IfcWindowStyleOperationEnum:
        ...
    
    @classmethod
    @property
    def TRIPLE_PANEL_BOTTOM(cls) -> IfcWindowStyleOperationEnum:
        ...
    
    @classmethod
    @property
    def TRIPLE_PANEL_TOP(cls) -> IfcWindowStyleOperationEnum:
        ...
    
    @classmethod
    @property
    def TRIPLE_PANEL_LEFT(cls) -> IfcWindowStyleOperationEnum:
        ...
    
    @classmethod
    @property
    def TRIPLE_PANEL_RIGHT(cls) -> IfcWindowStyleOperationEnum:
        ...
    
    @classmethod
    @property
    def TRIPLE_PANEL_HORIZONTAL(cls) -> IfcWindowStyleOperationEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcWindowStyleOperationEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcWindowStyleOperationEnum:
        ...
    
    ...

class IfcWorkControlTypeEnum:
    '''IfcWorkControlTypeEnum'''
    
    @classmethod
    @property
    def ACTUAL(cls) -> IfcWorkControlTypeEnum:
        ...
    
    @classmethod
    @property
    def BASELINE(cls) -> IfcWorkControlTypeEnum:
        ...
    
    @classmethod
    @property
    def PLANNED(cls) -> IfcWorkControlTypeEnum:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcWorkControlTypeEnum:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcWorkControlTypeEnum:
        ...
    
    ...

