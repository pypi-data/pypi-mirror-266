import { {{cookiecutter.resource_plural}}Service } from './{{cookiecutter.resource_kebap}}.service.js';
import { BaseController, ResourceController } from '@alvast-bedankt/gg-core';

@ResourceController({{cookiecutter.resource_plural}}Service, {
  pagination: {
    sortableColumns: ['id'],
    defaultLimit: 20,
    defaultSortBy: [['createdAt', 'DESC']],
  },
})
export class {{cookiecutter.resource_plural}}Controller extends BaseController<{{cookiecutter.resource_plural}}Service> {}
