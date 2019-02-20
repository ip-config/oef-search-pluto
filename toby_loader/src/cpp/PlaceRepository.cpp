//
//  PlaceRepository.cpp
//  Nodeography
//
//  Created by Toby Simpson on 18/01/2018.
//  Copyright © 2018 Toby Simpson. All rights reserved.
//

#include <stdio.h>
#include "PlaceRepository.h"

PlaceRepository::PlaceRepository(const std::string &filename)
{
	Load(filename);
	return;
}


PlaceRepository::~PlaceRepository()
{

}

const bool PlaceRepository::GetRandomPlace(Place& out_place)
{
	if (m_Places.empty())
	{
		return (false);
	}
	out_place = m_Places.at(rand() % m_Places.size());
	return (true);
}

const bool PlaceRepository::Load(const std::string &path)
{
	// Now open:
  FILE* fp = fopen(path.c_str(), "rb");
	if (NULL == fp)
	{
		return (false);				// File not found
	}
	
	while (true)
	{
		Place thisPlace;
		
		uint8_t placeSize;
		if (1 != fread(&placeSize, sizeof(uint8_t), 1, fp))
		{
			break;
		}
		thisPlace.type = (Place::Type)placeSize;
		
		if (1 != fread(&thisPlace.longitude, sizeof(float), 1, fp))
		{
			break;
		}
		if (1 != fread(&thisPlace.latitude, sizeof(float), 1, fp))
		{
			break;
		}
		if (false == ReadString(fp, thisPlace.name))
		{
			break;
		}
		if (false == ReadString(fp, thisPlace.county))
		{
			break;
		}
		if (Place::Type::Village == thisPlace.type)
		{
			continue;
		}
		m_Places.push_back(thisPlace);
	}	// while (stuff)
	
	fclose(fp);
	return (true);
}

const bool PlaceRepository::ReadString(FILE* fp, std::string& out_string)
{
	out_string = "";
	uint16_t characters;
	if (1 != fread(&characters, sizeof(uint16_t), 1, fp))
	{
		return (false);
	}
	out_string = "";
	for (uint16_t i = 0; i < characters; ++i)
	{
		char thisCharacter;
		if (1 != fread(&thisCharacter, sizeof(char), 1, fp))
		{
			return (false);
		}
		out_string += thisCharacter;
	}
	return (true);
}
