# <picture><source media="(prefers-color-scheme: dark)" srcset="https://github.com/Sayad-Uddin-Tahsin/Rotary-School-Student-Management/blob/main/Assets/Logo%20Light.png?raw=true"><img alt="Logo" src="https://github.com/Sayad-Uddin-Tahsin/Rotary-School-Student-Management/blob/main/Assets/Logo%20Dark.png?raw=true" height=40 width=40></picture>  Rotary School Student Management

Rotary School Student Management is a Software made for Rotary School Khulna for organizing the Student Information in a Digital Way! With this software, Student Information can be easily managed for different classes and sections.

## How it works?
Only need for this software is seemless internet connection. This software uses a Cloud Database to store student information. It has a security PIN system to keep the data secured from unauthorized access of the Software. Here's a diagram represents the Software:
```mermaid
graph TD;
    S["Splash Screen"]
    PW["PIN Authorization"]
    PM["PIN Matching"]
    subgraph MWG["Main Window"]
      NCB["New Class Button"]
      CL["Class List"]
      SB["Settings Button"]
    end
    subgraph NCW["New Class Window"]
      SVB["Save Button"]
    end
    subgraph DB["Database"]
      DBIFS["Information Stored Here"]
    end
    subgraph CW["Class Window"]
      SECL["Section List"]
      RMVCB["Remove Class Button"]
    end
    subgraph STLW["Student List Window"]
      SSTL["Section Students List"]
      ASTB["Add Student Button"]
      RMVSB["Remove Section Button"]
    end
    subgraph SIEW["Student Information Entry Window"]
      SIEWIF["Student Information Entry Fields"]
      SIEWSB["Save Student Button"]
    end
    subgraph STIW["Student Information Window"]
      STIF["Showing Student Information on different fields"]
      STUIB["Update Student Information Button"]
      RMVSTB["Remove Student Button"]
    end
    subgraph SW["Settings Window"]
        CTAMS["Appearence & Color Theme Settings"]
        PS["PIN Settings"]
        PV["PIN Validation"]
    end
    subgraph AW["About Window"]
        DI["Developer Informtion"]
        OI["Other Informtion"]
    end

    S --> PW;
    PW --> PM;
    PM -- Incorrect --> PW;
    PM -- Correct --> MWG;
    NCB -- Creating New Class --> NCW;
    SVB -- Adding New Class --> DB;
    SVB -- Updating Class List --> MWG;
    CL -- Showing Selected Class --> CW;
    RMVCB -- Update --> DB;
    RMVCB -- Redirection with Update --> MWG;
    SECL -- Showing Selected Section --> STLW;
    RMVSB -- Update --> DB;
    RMVSB -- Redirection with Update --> CW;
    ASTB -- Redirecting --> SIEW;
    SIEWSB -- Redirection with Update --> STLW;
    SIEWSB -- Update --> DB;
    SSTL -- Showing Selected Student Information --> STIW;
    STUIB -- Redirecting to Update Information --> SIEW;
    RMVSTB -- Redirection with Update --> STLW;
    RMVSTB -- Update --> DB;
    SB --> SW;
    PS -- PIN Validation --> PV;
    PV --> DB;
    PV -- Failed --> PS;
```

## Installation
The installer for the Rotary School Student Management Software will require a unique Serial Key to access. This approach is taken in the interest of user privacy and security to ensure that sensitive student data remains protected and in compliance with privacy regulations. As such, the installer will not be made publicly available.

We prioritize the security and privacy of student data and appreciate your understanding in this matter.

## License
This project is licensed under the [MIT License](./LICENSE).
