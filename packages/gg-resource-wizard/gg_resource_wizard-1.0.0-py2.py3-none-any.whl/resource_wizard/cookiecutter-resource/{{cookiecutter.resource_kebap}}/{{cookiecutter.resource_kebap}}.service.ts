import { Injectable } from '@nestjs/common';
import { ResourceService } from '@alvast-bedankt/gg-core';
import { {{cookiecutter.resource_singular}} } from './entities/{{cookiecutter.resource_kebap}}.entity.js';

@Injectable()
export class {{cookiecutter.resource_plural}}Service extends ResourceService.for({{cookiecutter.resource_singular}}) {}
