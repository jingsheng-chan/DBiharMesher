
#include <vtkSmartPointer.h>
#include <vtkPolyData.h>
#include <vtkGenericDataObjectReader.h>
#include <vtkDoubleArray.h>
#include <vtkUnsignedIntArray.h>
#include <vtkCellArray.h>

#include <vtkPointData.h>

#include <vtkXMLPolyDataWriter.h>
#include <vtkGenericDataObjectWriter.h>

#include <vtkXMLStructuredGridReader.h>

#include "vtkCentrelinePartitioner.h"
#include "wrapDbiharConfig.h"

#include "showPolyData.h"

int main(int argc, char* argv[]) {

	std::cout << "Starting " << __FILE__ << std::endl;

	vtkSmartPointer<vtkGenericDataObjectReader> vesselCentrelineReader = vtkSmartPointer<vtkGenericDataObjectReader>::New();
	vesselCentrelineReader->SetFileName((std::string(TEST_DATA_DIR) + "/227A_CentrelineResampled_4ECs.vtk").c_str());
	vesselCentrelineReader->Update();

	vtkPolyData *vesselCentreline = vtkPolyData::SafeDownCast(vesselCentrelineReader->GetOutput());


	vtkSmartPointer<vtkCentrelinePartitioner> centrelinePartitioner = vtkSmartPointer<vtkCentrelinePartitioner>::New();
	centrelinePartitioner->SetInputData(vesselCentreline);
	centrelinePartitioner->SetPartitionLength(50);

	vtkSmartPointer<vtkIdList> EndPoints = vtkSmartPointer<vtkIdList>::New();
	int x = 4;
	switch(x)
	{
		case 0:
			EndPoints->InsertNextId(10);
			EndPoints->InsertNextId(40); // End points on same branch.
			break;

		case 1:
			EndPoints->InsertNextId(60); // Starting from a different cell, will ignore one side of the tree.
			break;

		case 2:
			EndPoints->InsertNextId(10);
			EndPoints->InsertNextId(1306);
			EndPoints->InsertNextId(1490); // Standard cropping of branches.
			break;

		case 3:
			EndPoints->InsertNextId(60);
			EndPoints->InsertNextId(1306); // Will incur a warning, 1306 will never be reached.
			break;

		case 4:
			EndPoints->InsertNextId(10);
			EndPoints->InsertNextId(60);
			EndPoints->InsertNextId(1370); // End points lie next to bifurcations.
			break;
	}

	centrelinePartitioner->SetEndPoints(EndPoints);

	centrelinePartitioner->Update();

	centrelinePartitioner->Print(std::cout);

	writePolyData(centrelinePartitioner->GetOutput(), "partitionedCentreline.vtp");

	return EXIT_SUCCESS;
}

