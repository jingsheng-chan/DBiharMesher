#include <stdlib.h>

#include <vtkSmartPointer.h>
#include <vtkPolyData.h>
#include <vtkSubdivideQuadBrick.h>
#include <vtkXMLPolyDataReader.h>
#include <vtkIdList.h>

#include "wrapDbiharConfig.h"
#include "vtkDbiharStatic.h"


int main(int argc, char* argv[]) {

	std::cout << "Starting " << __FILE__ << std::endl;

	vtkSmartPointer<vtkXMLPolyDataReader> pointsReader = vtkSmartPointer<vtkXMLPolyDataReader>::New();
	pointsReader->SetFileName((std::string(TEST_DATA_DIR) + "/test/testSubdivideQuadBrick.vtp").c_str());

	pointsReader->Update();
	vtkSmartPointer<vtkPolyData> pd = vtkSmartPointer<vtkPolyData>::New();
	pd->DeepCopy(pointsReader->GetOutput());
	vtkSmartPointer<vtkSubdivideQuadBrick> subdivideQuadFilter = vtkSmartPointer<vtkSubdivideQuadBrick>::New();
	vtkSmartPointer<vtkPolyData> pointsData = vtkSmartPointer<vtkPolyData>::New();
	vtkSmartPointer<vtkIdList> pointsList = vtkSmartPointer<vtkIdList>::New();

	vtkSmartPointer<vtkPoints> points = vtkSmartPointer<vtkPoints>::New();
	pd->GetCellPoints(0,pointsList);
	points->SetNumberOfPoints(4);
	points->SetPoint(0,pd->GetPoint(pointsList->GetId(0)));
	points->SetPoint(1,pd->GetPoint(pointsList->GetId(1)));
	points->SetPoint(2,pd->GetPoint(pointsList->GetId(2)));
	points->SetPoint(3,pd->GetPoint(pointsList->GetId(3)));
	pointsData->SetPoints(points);
	subdivideQuadFilter->SetInputData(pointsData);
	subdivideQuadFilter->SetColumns(4);
	subdivideQuadFilter->SetRows(52);
	subdivideQuadFilter->SetCellType(vtkDbiharStatic::SMC);
	subdivideQuadFilter->Update();

	vtkDbiharStatic::ShowPolyData(subdivideQuadFilter->GetOutput());
#if 1
	vtkDbiharStatic::WritePolyData(subdivideQuadFilter->GetOutput(), "31.vtp");
#endif

	std::cout << "Exiting " << __FILE__ << std::endl;

	return EXIT_SUCCESS;
}
