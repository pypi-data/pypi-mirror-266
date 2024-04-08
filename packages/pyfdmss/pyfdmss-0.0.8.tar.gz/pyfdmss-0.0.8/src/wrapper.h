#pragma once

#include "stdafx.h"
#include "EnvCaseGenerator.h"
#include "Codegen.h"
#include "PbcOverdozenMicroperm.h"
#include "MouseFuncX.h"
#include "MouseFuncY.h"
#include "MouseFuncZ.h"
#include "OverdozenPermsolver.h"
#include "tinyxml.h"


void SolveImpl(CmdLineParameters *io_filenames)
{
	OverdozenPermsolver ps;
	ps.SetCmdLineParameters(io_filenames);

	float vel(0.0), squareFactor(0.0), permeability(0.0), error(0.0), limit_triggered(1.0);

	if (ps.ReadFailo(io_filenames->configFileName, io_filenames->imageFileName) == true)
	{
		printf("File loaded successfully\n");
		limit_triggered = 0.0;
		vel = ps.launch();
		squareFactor = ps.GetSquareFactor();
		permeability = ps.GetPermeability();
		error = ps.GetAugeCriterionError();
	}

	TiXmlDocument doc;
	TiXmlDeclaration *decl = new TiXmlDeclaration("1.0", "", "");
	doc.LinkEndChild(decl);
	TiXmlElement *rootElem = new TiXmlElement("OverdozenPermsolverOutput");

	TiXmlElement *iLimiterTriggered = new TiXmlElement("LimiterTriggered");
	iLimiterTriggered->SetDoubleAttribute("value", limit_triggered);
	TiXmlElement *iPermeabilityM2 = new TiXmlElement("Permeability_micrometer2");
	iPermeabilityM2->SetDoubleAttribute("value", permeability);
	TiXmlElement *iPermeabilityMD = new TiXmlElement("Permeability_mD");
	iPermeabilityMD->SetDoubleAttribute("value", permeability * OverdozenPermsolver::MILLIDARCY_CONVERT_RATE);
	TiXmlElement *iAverageVelocity = new TiXmlElement("AverageVelocity");
	iAverageVelocity->SetDoubleAttribute("value", vel);
	TiXmlElement *iRelativeError = new TiXmlElement("RelativeError");
	iRelativeError->SetDoubleAttribute("value", error);
	rootElem->LinkEndChild(iAverageVelocity);
	rootElem->LinkEndChild(iPermeabilityM2);
	rootElem->LinkEndChild(iPermeabilityMD);
	rootElem->LinkEndChild(iRelativeError);
	rootElem->LinkEndChild(iLimiterTriggered);

	printf("Average velocity, micrometers/sec = %.6f\n", vel);
	printf("Average velocity within pore space, micrometers/sec = %.6f\n", vel * squareFactor);
	printf("Permeability, sq micrometers = %.6f\n", permeability);
	printf("Permeability, mD = %.6f\n", permeability * OverdozenPermsolver::MILLIDARCY_CONVERT_RATE);
	printf("Open pore space fraction at inlet = %.6f\n", 1.0 / squareFactor);
	printf("Relative error = %.6f\n", error);

	const char *output_fnames[] = {
		io_filenames->velXFileName,
		io_filenames->velYFileName,
		io_filenames->velZFileName,
		io_filenames->pressuresFileName,
		io_filenames->fullVelsFileName};

	ps.printVelPrsFieldsCustom(output_fnames);

	doc.LinkEndChild(rootElem);
	doc.SaveFile(io_filenames->summaryFileName);
}

void run(std::string config_path = std::string("config.xml"), 
		 std::string image_path = std::string("image3d.raw"),
		 std::string summary_path = std::string("output.txt"),
         std::string velx_path = std::string("/dev/null"), 
		 std::string vely_path = std::string("/dev/null"), 
		 std::string velz_path = std::string("/dev/null"),
         std::string pressure_path = std::string("/dev/null"),
		 std::string full_vel_path = std::string("/dev/null"), 
		 std::string comp_vel_path = std::string("/dev/null"),
         std::string log_path = std::string("/dev/null")) {

	CmdLineParameters io_filenames (
		config_path.data(),
		image_path.data(),
		summary_path.data(),
		velx_path.data(),
		vely_path.data(),
		velz_path.data(),
		pressure_path.data(),
		full_vel_path.data(),
		comp_vel_path.data(),
		log_path.data());
	SolveImpl(&io_filenames);
	return;
}
