import { Test, TestingModule } from '@nestjs/testing';
import { {{cookiecutter.resource_plural}}Controller } from './{{cookiecutter.resource_kebap}}.controller.js';
import { {{cookiecutter.resource_plural}}Service } from './{{cookiecutter.resource_kebap}}.service.js';

describe('{{cookiecutter.resource_plural}}Controller', () => {
  let controller: {{cookiecutter.resource_plural}}Controller;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      controllers: [{{cookiecutter.resource_plural}}Controller],
      providers: [{{cookiecutter.resource_plural}}Service],
    }).compile();

    controller = module.get<{{cookiecutter.resource_plural}}Controller>({{cookiecutter.resource_plural}}Controller);
  });

  it('should be defined', () => {
    expect(controller).toBeDefined();
  });
});
