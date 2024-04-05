import numpy as np
import pydicom
from pathlib import Path


file = "/home/cavriley/programs/dcm-classifier/tests/testing_data/anonymized_testing_data/anonymized_data/1/DICOM/1.3.12.2.1107.5.1.4.3024295249861856527476734919304407350-1-1-mvhslo.dcm"

ds = pydicom.dcmread(file, stop_before_pixels=True)

ds.PixelBandwidth = ""
ds.EchoTime = ""
ds.InversionTime = ""
ds.FlipAngle = ""
ds.ImagingFrequency = ""
ds.RepetitionTime = ""
ds.SAR = ""
ds.ScanningSequence = ""
ds.SequenceVariant = ""
ds.SliceThickness = ""
ds.PixelSpacing = ""
ds.ImageOrientationPatient = ""
ds.ImageType = ""
ds.Manufacturer = ""
ds.ContrastBolusAgent = ""
# ds.Diffusionb_value = np.nan
# ds.Diffusionb_valueMax = np.nan
ds.EchoNumbers = ""
ds.EchoTrainLength = ""
ds.InPlanePhaseEncodingDirection = ""
ds.dBdt = ""
ds.MRAcquisitionType = ""
ds.NumberOfAverages = ""
ds.VariableFlipAngleFlag = ""
ds.AcquisitionTime = ""
ds.SeriesNumber = ""

print(ds)
path = Path(
    "/home/cavriley/programs/dcm-classifier/tests/testing_data/anonymized_testing_data/invalid_data"
)
assert path.exists()
pydicom.dcmwrite(
    path / "no_valid_fields.dcm",
    ds,
)
