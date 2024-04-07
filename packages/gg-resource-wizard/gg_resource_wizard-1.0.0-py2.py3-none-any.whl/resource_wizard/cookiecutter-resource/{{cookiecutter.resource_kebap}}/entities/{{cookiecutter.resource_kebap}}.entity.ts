import {ResourceEntity, UserRole} from "@alvast-bedankt/gg-core";
import {Entity} from "typeorm";

@Entity()
export class {{cookiecutter.resource_singular}} extends ResourceEntity<{{cookiecutter.resource_singular}}> {
}
