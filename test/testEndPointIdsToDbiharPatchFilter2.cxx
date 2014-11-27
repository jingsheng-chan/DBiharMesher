
#include <map>

#include <vtkSmartPointer.h>
#include <vtkPolyData.h>
#include <vtkGenericDataObjectReader.h>
#include <vtkDoubleArray.h>
#include <vtkMath.h>

#include <vtkPolyDataMapper.h>
#include <vtkActor.h>
#include <vtkRenderWindow.h>
#include <vtkRenderer.h>
#include <vtkRenderWindowInteractor.h>
#include <vtkInteractorStyleSwitch.h>

#include <vtkCellArray.h>
#include <vtkPointData.h>

#include <vtkXMLPolyDataWriter.h>
#include <vtkGenericDataObjectWriter.h>

#include <vtkXMLStructuredGridReader.h>

#include "showPolyData.h"

#include "vtkCentrelineData.h"
#include "vtkScalarRadiiToVectorsFilter.h"
#include "vtkEndPointIdsToDbiharPatchFilter.h"

#include "wrapDbiharConfig.h"

int main(int argc, char* argv[]) {

	std::cout << "Starting " << __FILE__ << std::endl;

#if 0
	vtkSmartPointer<vtkGenericDataObjectReader> vesselCentrelineReader = vtkSmartPointer<vtkGenericDataObjectReader>::New();
	//vesselCentrelineReader->SetFileName((std::string(TEST_DATA_DIR) + "/227A_Centreline.vtk").c_str());
	vesselCentrelineReader->SetFileName((std::string(TEST_DATA_DIR) + "/721A_Centreline.vtk").c_str());
	vesselCentrelineReader->Update();

	vtkPolyData *vesselCentreline = vtkPolyData::SafeDownCast(vesselCentrelineReader->GetOutput());

	vtkSmartPointer<vtkCentrelineData> centrelineSegmentSource = vtkSmartPointer<vtkCentrelineData>::New();
	centrelineSegmentSource->SetCentrelineData(vesselCentreline);

	vtkPolyData *resampledVesselCentreline = centrelineSegmentSource->GetOutput();
#else
	vtkSmartPointer<vtkGenericDataObjectReader> vesselCentrelineReader = vtkSmartPointer<vtkGenericDataObjectReader>::New();
	vesselCentrelineReader->SetFileName((std::string(TEST_DATA_DIR) + "/227A_CentrelineResampled_4ECs.vtk").c_str());
	//vesselCentrelineReader->SetFileName((std::string(TEST_DATA_DIR) + "/721A_CentrelineResampled_4ECs.vtk").c_str());
	vesselCentrelineReader->Update();

	vtkPolyData *resampledVesselCentreline = vtkPolyData::SafeDownCast(vesselCentrelineReader->GetOutput());
#endif

	vtkSmartPointer<vtkScalarRadiiToVectorsFilter> scalarRadiiToVectorsFilter = vtkSmartPointer<vtkScalarRadiiToVectorsFilter>::New();
	scalarRadiiToVectorsFilter->SetInputData(resampledVesselCentreline);
	scalarRadiiToVectorsFilter->Update();

	vtkPolyData *resampledVesselCentrelineWithRadii = scalarRadiiToVectorsFilter->GetOutput();

	vtkSmartPointer<vtkIdList> endPointIdsList = vtkSmartPointer<vtkIdList>::New();

#if 1
	// Bifurcation segment.
	endPointIdsList->InsertNextId(21);
	endPointIdsList->InsertNextId(79);
	endPointIdsList->InsertNextId(948);
	//endPointIdsList->InsertNextId(160);
	//endPointIdsList->InsertNextId(260);
	//endPointIdsList->InsertNextId(560);

#else
	// Straight segment.
	endPointIdsList->InsertNextId(350); //920);
	endPointIdsList->InsertNextId(450); //990);
#endif
	// TODO: Test 80 to 210 which spans accros a bifurcation.

	const double unitsConversionFactor = 1.0e-3;
	vtkSmartPointer<vtkDoubleArray> radiiArray = vtkDoubleArray::SafeDownCast(resampledVesselCentreline->GetPointData()->GetArray(vtkCentrelineData::RADII_ARR_NAME));
	double R = radiiArray->GetValue(endPointIdsList->GetId(0));
	R *= unitsConversionFactor; // R in m.

	double C = 2 * vtkMath::Pi() * R;

	const double ECLength = 65e-6; // m.
	const double SMCLength = 50e-6; // m.
	const unsigned int ECMultiple = 4;
	const unsigned int SMCMultiple = 4;

	double tmpDoubleVal = (C / 2.0) / (SMCLength * SMCMultiple);
	int tmpIntVal = vtkMath::Round(tmpDoubleVal);

	int numberOfRadialQuads = tmpIntVal;
	// Must be even.
	if((numberOfRadialQuads & 1) == 1)
	{
		if(tmpDoubleVal - (double)tmpIntVal > 0)
		{
			// Increment.
			numberOfRadialQuads++;
		}
		else
		{
			// Decrement.
			numberOfRadialQuads--;
		}
	}

	std::cout << numberOfRadialQuads << std::endl;

	vtkSmartPointer<vtkEndPointIdsToDbiharPatchFilter> idListToDbiharPatchFilter = vtkSmartPointer<vtkEndPointIdsToDbiharPatchFilter>::New();
	idListToDbiharPatchFilter->SetInputData(resampledVesselCentrelineWithRadii);
	idListToDbiharPatchFilter->SetNumberOfRadialQuads(numberOfRadialQuads);
	idListToDbiharPatchFilter->SetEndPointIdsList(endPointIdsList);
	idListToDbiharPatchFilter->Update();

	showPolyData(idListToDbiharPatchFilter->GetOutput(), NULL, 0.1);

	vtkSmartPointer<vtkXMLPolyDataWriter> meshWrtirer = vtkSmartPointer<vtkXMLPolyDataWriter>::New();
	meshWrtirer->SetInputData(idListToDbiharPatchFilter->GetOutput());
	meshWrtirer->SetFileName((std::string(argv[0]) + ".vtp").c_str());
	std::cout << "Writing " << meshWrtirer->GetFileName() << std::endl;
	meshWrtirer->Write();

	std::cout << "Exiting " << __FILE__ << std::endl;

	return EXIT_SUCCESS;
}
