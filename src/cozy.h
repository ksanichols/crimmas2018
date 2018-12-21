#ifndef COZY_H
#define COZY_H 

struct Thread;

Thread *getThread();

struct MultiThread;

int ThreadMultiplexer(MultiThread *target,
                      Thread      *tanglee);



#endif /* COZY_H */
