from matplotlib.pyplot import (plot, show, draw, pause)
from numpy import array, tanh, zeros, append
from numpy.random import random_sample
from math import exp
from random import shuffle


def dtanh(x):
    ''' Derivative of sigmoid above '''
    if abs(x) > 10:
        return 0
    return 4.0/(exp(x)+exp(-x))**2


class Neuron(object):
    """ Class neuron """
    def __init__(self, number_of_weights):
        self.weights = random_sample(number_of_weights)

    def proc(self, inputs):
        """ Inputs is an np.array that include bias """
        self.inputs = inputs
        self.u = self.inputs.dot(self.weights)
        return tanh(self.u)

    def backpropagation(self, error):
        """ error is error before multiplied by derivative """
        self.error = error*dtanh(self.u)
        self.weights += 0.1 * self.inputs * self.error


class Layer(object):
    """ Class layer """
    def __init__(self, number_of_neurons, inputs_per_neuron):
        """ inputs_per_neuron: doesn't consider bias """
        self.outputs = zeros(number_of_neurons)
        self.neurons = []
        for neuron in range(number_of_neurons):
            self.neurons.append(Neuron(inputs_per_neuron+1))  # plus bias

    def proc(self, inputs):
        """
        Inputs is a np.array that include bias
        Outputs is a np.array that doesn't consider bias
        """
        for idx, neuron in enumerate(self.neurons):
            self.outputs[idx] = neuron.proc(inputs)
        return self.outputs


class OutputLayer(Layer):
    def backpropagation(self, obt, desired):
        """ obt and desired are np.arrays """
        for neuron, o, d in zip(self.neurons, obt, desired):
            neuron.backpropagation(d-o)


class HiddenLayer(Layer):
    def backpropagation(self, next_layer):
        """ next_layer is the next_layer """
        for idx, neuron in enumerate(self.neurons):
            error = 0.0
            for next_neuron in next_layer.neurons:
                error += next_neuron.error*next_neuron.weights[idx]
            neuron.backpropagation(error)


class MLP(object):
    """ Multilayer Perceptron class """
    def __init__(self, layer_list):
        """
        layer_list: a list, the number of elements in the list is the number
        of layers, and the value of each element is the numer of neurons in
        that layer, e.g. [2,2,1] means 2 input layers, 2 hidden layers and
        1 output layer
        """
        self.bias = -1
        self.layers = []
        inputs_per_neuron = layer_list[0]
        # actually we doesn't have an input layer
        for number_of_neurons in layer_list[1:-1]:
            self.layers.append(HiddenLayer(number_of_neurons,
                                           inputs_per_neuron))
            inputs_per_neuron = number_of_neurons
        self.layers.append(OutputLayer(layer_list[-1], inputs_per_neuron))

    def train(self, input, desired):
        """
        input: a list containing the input values, doesn't consider bias
        desired: a list containing the desired values
        """
        print input, desired
        obt = self.proc(input)
        # print self.calc_final_err(obt, desired)
        self.backpropagation(obt, desired)
        return obt

    def calc_final_err(self, output, desired):
        """ output and desired are np.arrays """
        squared_errors = (desired - output)**2
        return squared_errors.sum()

    def backpropagation(self, obt, desired):
        """ obt y desired son listas """
        # Output layer
        self.layers[-1].backpropagation(obt, desired)
        # Hidden layers
        next_layer = self.layers[-1]
        for layer in self.layers[-2::-1]:
            layer.backpropagation(next_layer)
            next_layer = layer

    def proc(self, inputs):
        """
        This function is used in production.
        Returns the output of the mlp for the given input list
        input: list, doesn't consider bias
        """
        for layer in self.layers:
            inputs = append(inputs, self.bias)
            inputs = layer.proc(inputs)
        return inputs


if __name__ == '__main__':
    DATA = array([[0, 0, 0],
                  [0, 1, 1],
                  [1, 0, 1],
                  [1, 1, 0]])

    mlp = MLP([2, 2, 1])
    for epoch in range(2500):
        pos = range(4)
        shuffle(pos)
        for i in pos:
            input = DATA[i, :-1]
            desired = DATA[i, -1:]
            mlp.train(input, desired)

    print 0, 0, mlp.proc([0, 0])
    print 1, 0, mlp.proc([1, 0])
    print 0, 1, mlp.proc([0, 1])
    print 1, 1, mlp.proc([1, 1])