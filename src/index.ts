import * as readline from 'readline';

title();
console.log(`La ruta del archivo proporcionada es: ${await askFilePath()}`);

function title(): string {
    return `
    l)L                                  l)L                                          
    l)                                   l)                                          
    l)   o)OOO   g)GGG           c)CCCC  l)  e)EEEEE a)AAAA  n)NNNN  e)EEEEE  r)RRR  
    l)  o)   OO g)   GG ####### c)       l)  e)EEEE   a)AAA  n)   NN e)EEEE  r)   RR 
    l)  o)   OO g)   GG         c)       l)  e)      a)   A  n)   NN e)      r)      
   l)LL  o)OOO   g)GGGG          c)CCCC l)LL  e)EEEE  a)AAAA n)   NN  e)EEEE r)      
                     GG                                                              
                g)GGGG                                                  
    `;
}

function askFilePath(): Promise<string> {
    const rl = readline.createInterface({
        input: process.stdin,
        output: process.stdout
    });

    return new Promise((resolve) => {
        rl.question('Por favor, introduce la ruta del log que quiere tratar: ', (filePath) => {
            rl.close();
            resolve(filePath);
        });
    });
}