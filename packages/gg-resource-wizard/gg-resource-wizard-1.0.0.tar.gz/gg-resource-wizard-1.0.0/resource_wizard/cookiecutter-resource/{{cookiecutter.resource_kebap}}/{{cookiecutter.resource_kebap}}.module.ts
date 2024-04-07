import { {{cookiecutter.resource_plural}}Controller } from './{{cookiecutter.resource_kebap}}.controller.js';
import { ResourceModule } from '@alvast-bedankt/gg-core';

@ResourceModule({ controllers: [{{cookiecutter.resource_plural}}Controller] })
export class {{cookiecutter.resource_plural}}Module {}
