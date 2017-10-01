//
// Created by Per-Arne on 24.02.2017.
//

#pragma once

#include <vector>
#include <memory>
#include <map>
#include <set>
#include "../Constants.h"
#include "../environment/Tile.h"
#include "../state/StateManager.h"
#include "../Config.h"
#include "../util/Position.h"


class Player;
class BaseState;



class Unit{
private:
    static int gId;
public:
	Unit(Player *player);
	Unit() {}

    // Graphics
    double animationInterval = 1 * 10;
    int animationTimer = 0;
    int animationIterator = 0;

    int id;
	Constants::Unit typeId;
    int health;
    int health_max;
    int direction;


    int groundUnit;
    int waterUnit;

    int damageMin = -1;
    int damageMax = -1;
    int damageRange = -1;
    int damagePiercing = -1;
    int armor = -1;

    int lumberCarry = 0;
    int goldCarry = 0;
    int oilCarry = 0;
    int carryCapacity = 10;
    std::vector<Constants::Unit> buildInventory;
    int speed;
    int sight;

    bool canHarvest;
    bool canAttack;
    bool canMove;
    bool military;
    bool structure;
    bool recallable = false;

    int lumberCost;
    int goldCost;
    int oilCost;

    int foodProduction;
    int foodConsumption;

    int width;
    int height;

    std::string name;


    Player *player_;


    // State attributes

	// Spawning
	int spawnDuration;
	int spawnTileID = -1;
	int builtByID = -1;
	Unit &getBuiltBy();
	Tile &getSpawnTile();


    // Harvesting
    double harvestInterval = .5 * 10;
    int harvestTimer;
    int harvestIterator;
    int harvestTargetID = -1;
	Tile *getTile(int tileID);
    std::set<int> getVisionTileIDs();

    // Building
    int spawnTimer;
    int buildEntityID = -1;
	Unit &getBuildEntity();
    int buildTimer;

    // Combat
    int combatTargetID = -1;
	Unit &getCombatTarget();
    int combatTimer = 1000;
    double combatInterval = 1 * 10;

    // Walking
    int walking_timer = 0;
    std::vector<Tile *> walking_path;
    int walkingGoalID = -1;
	int stepsLeft = 0; // If value is 0 it is ignored. However, Walking is transitioned when stepsLeft = 1 (Which decrements it to 0)
    double walking_interval = 1 * 5;


    Tile *tile = NULL;
    StateManager* stateManager;
	std::shared_ptr<BaseState> state = NULL;

    std::vector<Constants::State> stateList;



    bool build(int idx);
    void spawn(Tile &x, int initValue);
    void despawn();
    void update();
	Tile * centerTile();
    void enqueueState(std::shared_ptr<BaseState> state);
    void transitionState();
    void transitionState(std::shared_ptr<BaseState> nextState);
    void setPosition(Tile &tile);
    void rightClick(Tile &tile);
    void move(Tile &targetTile);
    void attack(Tile &tile);
    void harvest(Tile &tile);
    int distance(Tile &tile);
    int distance(Unit & unit);
	Position distanceVector(Tile &target);


    void clearTiles();

    Unit  *closestRecallBuilding();


    bool isDead();

    void afflictDamage(int dmg_);

    int getDamage(Unit &target);

    Position worldPosition;

    void setDirection(int newX, int newY);
    void setDirection(Position &dir);

    void moveRelative(int x, int y);

    void rightClickRelative(int x, int y);

    bool removedFromGame = false;

	bool operator==(int id) const;

	void tryMove(int16_t x, int16_t y);
	void tryAttack();
	void tryHarvest();
	

};

