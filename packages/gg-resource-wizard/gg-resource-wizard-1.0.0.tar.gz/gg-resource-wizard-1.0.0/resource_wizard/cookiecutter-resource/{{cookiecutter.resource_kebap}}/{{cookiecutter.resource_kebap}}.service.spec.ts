import { Test, TestingModule } from '@nestjs/testing';
import { {{cookiecutter.resource_plural}}Service } from './{{cookiecutter.resource_kebap}}.service.js';

describe('{{cookiecutter.resource_plural}}Service', () => {
  let service: {{cookiecutter.resource_plural}}Service;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      providers: [{{cookiecutter.resource_plural}}Service],
    }).compile();

    service = module.get<{{cookiecutter.resource_plural}}Service>({{cookiecutter.resource_plural}}Service);
  });

  it('should be defined', () => {
    expect(service).toBeDefined();
  });
});
